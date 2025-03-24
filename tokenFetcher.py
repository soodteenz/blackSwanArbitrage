# imports
from getPool import extractAddress
import os
from web3 import Web3, HTTPProvider
from dotenv import load_dotenv, find_dotenv
from ratelimiter import RateLimiter
from pycoingecko import CoinGeckoAPI
from polygonscan import PolygonScan
#from etherscan import Etherscan
#from etherscan import Snowtrace
#from bscscan import BscScan

# LOADING the .env file
load_dotenv(find_dotenv())


# the parameter is the unique tx hash of the tx being queries & the specific blockexplorer the tx is coming from
def getTokens(txHash:str, blockExplorer:str):
    # checks the blockexploer given arguement from TA and determines which blockchain to connect to
    match blockExplorer:
        case 'polygonscan.com/tx/':
            # instantiate a web3 remote provider
            endPoint = os.getenv('endpoint')
            try:
                w3 = Web3(HTTPProvider(endPoint))
            except Exception as err:
                print(err)


    # the tx receipt for to gather all tokens which were traded
    txReceipt = w3.eth.get_transaction_receipt(txHash)
    tokenAdressList = [str(eachElement.address) for eachElement in txReceipt.logs]
    # this takes each element inside of the list and map it a dictionary deleting any   duplicates and assign NO values inside of the dictionary - from stackoverflow
    uniqueTokenAddressList = list(dict.fromkeys(tokenAdressList))
    # dict for storing token details
    tokenDict = {}
    for eachAddress in uniqueTokenAddressList:
        # we need the unique abi of each specific address
        match blockExplorer:
            case 'polygonscan.com/tx/':
                with PolygonScan(os.getenv('polyscan'),False) as blockScan:
                    abi = blockScan.get_contract_abi(eachAddress)
            case 'etherscan.io/tx/':
                raise Exception('Resolve Conflicts <- Not Working atm')
                eth = Etherscan(os.getenv('etherscan'))
                abi = eth.get_contract_abi(eachAddress)
            case 'bscscan.com/tx/':
                raise Exception('BSCScan Has NOT Yet Been Implemented')
                with BscScan(os.getenv('bscscan')) as blockScan:
                    abi = blockScan.get_contract_abi(eachAddress)
            case 'snowtrace.io/tx/':
                raise Exception('SnowTrace Has Conflicts With Etherscan')
                avax = Snowtrace(os.getenv('snowtrace'))
                abi = avax.get_contract_abi(eachAddress)

        # the contract of the given address
        tokenContract = w3.eth.contract(address=eachAddress, abi=abi)
        
        # API rate limiter to ensure I don't go over my calls per second
        rate_limiter = RateLimiter(max_calls=3, period=2)
        
        with rate_limiter:
            # contrainsts to look for ONLYERC20 Tokens based on what is usually found in them 
            erc20TokenFunctionList = ['<Function balanceOf(address)>', '<Functionname()>', '<Function totalSupply()>', '<Function symbol()>', '<Functiondecimals()>', '<Function transfer(address,uint256)>']

            # gets ALL functions belonging to a smart contract address, turns them into strings for better parsing
            allTokenFunctionsList = [str(eachElement) for eachElement in tokenContract.all_functions()]
            # using the allTokenFunctionsList it finds the matching functions with erc20TokenFunctionList
            if set(erc20TokenFunctionList).intersection(allTokenFunctionsList):
                tokenSymbol = tokenContract.functions.symbol().call()
                tokenName = tokenContract.functions.name().call()
                tokenDecimals = tokenContract.functions.decimals().call()
                cg = CoinGeckoAPI()
                if cg.search(tokenSymbol)['coins'] != []:
                    #tokenDict.update({f"{tokenSymbol}":{tokenName,tokenDecimals,eachAddress}})
                    tokenDict.update(
                        {tokenSymbol: {'name':tokenName, 'address': eachAddress, 'decimals': tokenDecimals}}
                    )

    print(tokenDict)
    extractAddress(tokenDict)
