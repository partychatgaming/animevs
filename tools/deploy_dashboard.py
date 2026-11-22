"""Publish the dashboard.

Amplify Hosting can serve static files and Node servers. This dashboard is a
Python process, so it runs on Elastic Beanstalk, with CloudFront in front for
HTTPS. animevsplus.me is not a registered domain, so the public address is the
CloudFront hostname this script prints. Secrets stay out of the output except
for a sign-in password the first time one is created.
"""

import secrets
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import boto3
from botocore.exceptions import ClientError
from decouple import Config, RepositoryEnv

ROOT = Path(__file__).resolve().parents[1]
REGION = "us-east-2"
APP = "animevs-dashboard"
ENV_NAME = "animevs-dashboard"
STACK = "64bit Amazon Linux 2023 v4.14.4 running Python 3.11"
ACCOUNT = "010526260578"
CACHE_DISABLED = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
ALL_VIEWER = "216adef6-5c7f-47e4-b989-5492eafa07d3"
SERVICE_ROLE = f"arn:aws:iam::{ACCOUNT}:role/service-role/aws-elasticbeanstalk-service-role"
INSTANCE_PROFILE = "aws-elasticbeanstalk-ec2-role"

SKIP_DIRS = {".git", ".venv", "__pycache__", ".cursor", ".amplify-hosting"}
SKIP_FILES = {".env", ".DS_Store"}


def env_file():
    path = ROOT / ".env"
    if not path.exists():
        raise SystemExit(".env is missing. The deploy needs it on this machine and does not commit it.")
    return path


def settings():
    return Config(RepositoryEnv(str(env_file())))


def ensure_dashboard_secrets(cfg):
    path = env_file()
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    created = []
    for key, maker in (
        ("DASHBOARD_SECRET", lambda: secrets.token_hex(32)),
        ("DASHBOARD_PASSWORD", lambda: secrets.token_urlsafe(18)),
    ):
        if not cfg(key, default="").strip():
            value = maker()
            text += f"{key}={value}\n"
            created.append((key, value))
    if created:
        path.write_text(text, encoding="utf-8")
    return created


def environment_properties(cfg):
    raw = env_file().read_text(encoding="utf-8")
    values = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value.strip().strip('"').strip("'")
    values["DASHBOARD_HTTPS"] = "1"
    values["ENV"] = values.get("ENV") or "production"
    missing = [key for key in ("MONGO_LOGIN", "DASHBOARD_PASSWORD", "DASHBOARD_SECRET") if not values.get(key)]
    if missing:
        raise SystemExit("Missing in .env: " + ", ".join(missing))
    return values


def bundle():
    target = ROOT / ".deploy" / "dashboard.zip"
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            parts = set(rel.parts)
            if parts & SKIP_DIRS or rel.name in SKIP_FILES or rel.suffix == ".pyc":
                continue
            if rel.parts[:2] == ("assets", "card_overlays"):
                continue
            if rel.name.startswith(".card_art_state"):
                continue
            if ".deploy" in rel.parts:
                continue
            archive.write(path, rel.as_posix())
        names = archive.namelist()
    if ".env" in names or any(name.endswith("/.env") for name in names):
        raise SystemExit("Refusing to upload because the bundle contains .env")
    print(f"bundle {target.stat().st_size // 1024} KB, {len(names)} files")
    return target


def version_label():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        sha = "local"
    return time.strftime(f"dash-%Y%m%d%H%M%S-{sha}")


def option(namespace, name, value):
    return {"Namespace": namespace, "OptionName": name, "Value": value}


def base_options():
    options = [
        option("aws:elasticbeanstalk:environment", "EnvironmentType", "LoadBalanced"),
        option("aws:elasticbeanstalk:environment", "LoadBalancerType", "application"),
        option("aws:elasticbeanstalk:environment", "ServiceRole", SERVICE_ROLE),
        option("aws:autoscaling:launchconfiguration", "IamInstanceProfile", INSTANCE_PROFILE),
        option("aws:autoscaling:launchconfiguration", "InstanceType", "t3.small"),
        option("aws:autoscaling:launchconfiguration", "RootVolumeType", "gp3"),
        option("aws:autoscaling:launchconfiguration", "RootVolumeSize", "16"),
        option("aws:autoscaling:asg", "MinSize", "1"),
        option("aws:autoscaling:asg", "MaxSize", "1"),
        option("aws:elasticbeanstalk:healthreporting:system", "SystemType", "enhanced"),
        option("aws:elasticbeanstalk:command", "DeploymentPolicy", "AllAtOnce"),
        option("aws:elasticbeanstalk:environment:process:default", "HealthCheckPath", "/health"),
        option("aws:elasticbeanstalk:environment:process:default", "MatcherHTTPCode", "200"),
        option("aws:elasticbeanstalk:managedactions", "ManagedActionsEnabled", "true"),
        option("aws:elasticbeanstalk:managedactions", "PreferredStartTime", "Tue:09:00"),
        option("aws:elasticbeanstalk:managedactions:platformupdate", "UpdateLevel", "minor"),
    ]
    return options


def property_options(values):
    space = "aws:elasticbeanstalk:application:environment"
    return [option(space, key, value) for key, value in sorted(values.items())]


def find_distribution(cf):
    marker = None
    while True:
        page = cf.list_distributions(Marker=marker)["DistributionList"] if marker else cf.list_distributions()["DistributionList"]
        for item in page.get("Items") or []:
            if item.get("Comment") == APP:
                return item
        if not page.get("IsTruncated"):
            return None
        marker = page.get("NextMarker")


def distribution_config(cname, caller):
    return {
        "CallerReference": caller,
        "Comment": APP,
        "Enabled": True,
        "PriceClass": "PriceClass_100",
        "HttpVersion": "http2",
        "IsIPV6Enabled": True,
        "Origins": {"Quantity": 1, "Items": [{
            "Id": "dashboard",
            "DomainName": cname,
            "CustomOriginConfig": {
                "HTTPPort": 80,
                "HTTPSPort": 443,
                "OriginProtocolPolicy": "http-only",
                "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]},
                "OriginReadTimeout": 60,
            },
        }]},
        "DefaultCacheBehavior": {
            "TargetOriginId": "dashboard",
            "ViewerProtocolPolicy": "redirect-to-https",
            "AllowedMethods": {
                "Quantity": 7,
                "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
                "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
            },
            "CachePolicyId": CACHE_DISABLED,
            "OriginRequestPolicyId": ALL_VIEWER,
            "Compress": True,
        },
        "Restrictions": {"GeoRestriction": {"RestrictionType": "none", "Quantity": 0}},
        "ViewerCertificate": {"CloudFrontDefaultCertificate": True},
    }


def ensure_https(cname, caller):
    cf = boto3.client("cloudfront")
    found = find_distribution(cf)
    if found is None:
        created = cf.create_distribution(DistributionConfig=distribution_config(cname, caller))
        domain = created["Distribution"]["DomainName"]
        print(f"https://{domain}")
        return domain
    current = found["Origins"]["Items"][0]["DomainName"]
    if current != cname:
        config = cf.get_distribution_config(Id=found["Id"])
        body = config["DistributionConfig"]
        body["Origins"]["Items"][0]["DomainName"] = cname
        cf.update_distribution(Id=found["Id"], IfMatch=config["ETag"], DistributionConfig=body)
    print(f"https://{found['DomainName']}")
    return found["DomainName"]


def wait_ready(eb):
    for _ in range(80):
        env = eb.describe_environments(ApplicationName=APP, EnvironmentNames=[ENV_NAME])["Environments"]
        if not env:
            raise SystemExit("Environment disappeared while waiting.")
        current = env[0]
        status = current["Status"]
        health = current.get("Health", "")
        print(f"{status} {health}")
        if status == "Ready":
            if health in ("Red", "Severe"):
                raise SystemExit(f"Environment is Ready but health is {health}. Check the Beanstalk events.")
            return current
        if status in ("Terminated", "Terminating"):
            raise SystemExit("Environment terminated during deploy.")
        time.sleep(15)
    raise SystemExit("Timed out waiting for the environment.")


def main():
    cfg = settings()
    created = ensure_dashboard_secrets(cfg)
    values = environment_properties(Config(RepositoryEnv(str(env_file()))))
    archive = bundle()
    label = version_label()

    eb = boto3.client("elasticbeanstalk", region_name=REGION)
    s3 = boto3.client("s3", region_name=REGION)

    names = [item["ApplicationName"] for item in eb.describe_applications()["Applications"]]
    if APP not in names:
        eb.create_application(ApplicationName=APP, Description="Anime VS+ gameplay dashboard")

    bucket = eb.create_storage_location()["S3Bucket"]
    key = f"{APP}/{label}.zip"
    s3.upload_file(str(archive), bucket, key)
    eb.create_application_version(
        ApplicationName=APP,
        VersionLabel=label,
        SourceBundle={"S3Bucket": bucket, "S3Key": key},
        Process=True,
    )
    for _ in range(40):
        versions = eb.describe_application_versions(ApplicationName=APP, VersionLabels=[label])["ApplicationVersions"]
        status = versions[0]["Status"] if versions else ""
        if status == "PROCESSED":
            break
        if status == "FAILED":
            raise SystemExit("Beanstalk rejected the source bundle.")
        time.sleep(3)
    else:
        raise SystemExit("Timed out while Beanstalk checked the source bundle.")

    options = base_options() + property_options(values)
    existing = eb.describe_environments(ApplicationName=APP, EnvironmentNames=[ENV_NAME], IncludeDeleted=False)["Environments"]
    existing = [item for item in existing if item["Status"] != "Terminated"]
    if existing:
        print(f"updating {ENV_NAME} to {label}")
        eb.update_environment(ApplicationName=APP, EnvironmentName=ENV_NAME, VersionLabel=label, OptionSettings=options)
    else:
        print(f"creating {ENV_NAME} as {label}")
        eb.create_environment(
            ApplicationName=APP,
            EnvironmentName=ENV_NAME,
            Description="Anime VS+ gameplay dashboard",
            SolutionStackName=STACK,
            VersionLabel=label,
            CNAMEPrefix=ENV_NAME,
            OptionSettings=options,
        )
    current = wait_ready(eb)
    ensure_https(current["CNAME"], label)
    print(f"deployed {label}")
    for key, value in created:
        if key == "DASHBOARD_PASSWORD":
            print(f"new DASHBOARD_PASSWORD={value}")


if __name__ == "__main__":
    try:
        main()
    except ClientError as exc:
        error = exc.response.get("Error", {})
        raise SystemExit(f"{error.get('Code', 'ClientError')}: {error.get('Message', 'AWS rejected the request.')}") from None
