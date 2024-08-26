from bitcoinlib.wallets import Wallet, WalletError
from bitcoinlib.services.services import Service
import logging
from datetime import datetime

FEE = 223  # Fee in satoshis
DEBUG=False
NETWORK='testnet'

def setup_logging(log_level=logging.DEBUG, log_file=None):
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a handler for stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # If a log file is specified, create a file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set bitcoinlib logger to use this configuration
    bitcoinlib_logger = logging.getLogger('bitcoinlib')
    bitcoinlib_logger.setLevel(log_level)
    bitcoinlib_logger.propagate = True

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"debug_{current_time}.log"
setup_logging(log_level=logging.INFO, log_file=filename)

def check_transaction(wallet, txid):
    try:
        tx = wallet.gettransaction(txid)
        if tx:
            logging.info("Transaction found in wallet:")
            logging.info(tx.info())
            return True
        else:
            return False
    except Exception as e:
        logging.exception(f"Error checking transaction: {e}", e)
        return False
    
def update_wallet_data(wallet):
    logging.info(f"Updating wallet {wallet.name}")
    wallet.scan(scan_gap_limit=10)
    wallet.utxos_update()
    logging.info(f"DONE Updating wallet {wallet.name}")

def print_wallet_balance(wallet, service, name=""):
    balance_satoshi = wallet.balance()
    balance_btc = satoshi_to_btc(balance_satoshi)
    logging.info(f"Wallet {name} balance after scan: {balance_satoshi} satoshi")
    logging.info(f"Wallet {name} balance after scan: {balance_btc:.8f} BTC")
    # Get all addresses
    addresses = [key.address for key in wallet.keys()]
    # Manually check balance for each address
    total_balance = 0
    for address in addresses:
        address_info = service.getbalance(address)
        logging.info(f"Wallet: {name}, Address: {address}, Balance: {address_info} satoshi")
        total_balance += address_info
    logging.info(f"Total balance for wallet {name} from service: {total_balance} satoshi")
    logging.info("")

def print_wallet_transaction(wallet):
    # Print all transactions
    for t in wallet.transactions():
        logging.info(t.info())
        logging.info(f"Wallet {wallet.name} - Transaction {t.txid} - Status: {t.status}")

def satoshi_to_btc(satoshi):
    return satoshi / 100000000

# Function to convert BTC to satoshis
def btc_to_satoshi(btc):
    return int(btc * 100000000)


# Create or load a wallet
# Try to load the existing wallet, or create a new one if it doesn't exist
try:
    wallet = Wallet.create(name='test_wallet_1__XX', network=NETWORK)
    logging.info("Existing wallet loaded.")
    logging.info(f"Wallet network is {wallet.network.name}")
    logging.info(f"Sender Wallet address is {wallet.get_key().address}")
except WalletError as e:
    wallet = Wallet('test_wallet_1__XX')
    logging.info("New wallet created.")
    # logging.exception(e)
    # exit(1)

# Get a new address
address = wallet.get_key().address
logging.info(f"Your network {NETWORK} address is: {address}")

service = Service(network=NETWORK)


# Perform a thorough scan
#update_wallet_data(wallet)
#update_wallet_data(recipient_wallet)
# 
#print_wallet_balance(wallet, service, wallet.name)
#print_wallet_balance(recipient_wallet, service, recipient_wallet.name)
# 
#print_wallet_transaction(wallet)
#print_wallet_transaction(recipient_wallet)


# Make sure the wallet has some testnet coins
# You may need to use a testnet faucet to get some coins first
# Get user input for amount to send
#amount_btc = float(input("Enter the amount of BTC you want to send: "))
amount_btc = 0.00015534/3
amount_satoshi = btc_to_satoshi(amount_btc)

recipient_address = "bc1..." #recipient_wallet.get_key().address

logging.info(f"from {wallet.get_key().address} to {recipient_address}")
outputs = [(recipient_address, amount_satoshi)]
tx = wallet.send(outputs, fee=FEE, network=NETWORK, offline=DEBUG)
logging.info(tx)

# Retrieve the transaction details using the transaction ID
# transaction = wallet.gettransaction(txid)
# logging.info(transaction.info())
# logging.info(transaction.outputs())