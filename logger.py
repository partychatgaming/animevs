import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger object for your module
loggy = logging.getLogger(__name__)
