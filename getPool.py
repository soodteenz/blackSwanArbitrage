# IMPORTS
import requests
from bdexTest import arbitrage, main
from subprocess import call

# GLOBALS
aDicOfToken = {'WMATIC': {'name': 'Wrapped Matic', 'address': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270', 'decimals': 18}, 'MATIC': {'name': 'Matic Token', 'address': '0x0000000000000000000000000000000000001010', 'decimals': 18}, 'jCHF': {'name': 'Jarvis Synthetic Swiss Franc', 'address': '0xbD1463F02f61676d53fd183C2B19282BFF93D099', 'decimals': 18}, 'jEUR': {'name': 'Jarvis Synthetic Euro', 'address': '0x4e3Decbb3645551B8A19f0eA1678079FCB33fB4c', 'decimals': 18}, 'jGBP': {'name': 'Jarvis Synthetic British Pound', 'address': '0x767058F11800FBA6A682E73A6e79ec5eB74Fac8c', 'decimals': 18}}

# function to use requests.post to make an API call to the Kyberswap subgraph url
def getExchangePool_K(tokenDict: dict) -> None:
  """Extracts addresses given a dictionary of tokens

  Args:
      tokenDict (dict): Accepts the dictionary from tokenFetech.py to extract the addresses from the Tweet
  """

  token1Address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'

  api = 'https://api.thegraph.com/subgraphs/name/kybernetwork/kyberswap-elastic-matic'


  for eachToken, eachValue in tokenDict.items():
    token0Name = eachToken
    token0Address = eachValue['address']
    queryK = """
  {{
    token(id:"{token0Address}") {{
      symbol,
      name,
      whitelistPools (orderBy: feeTier, orderDirection: asc, where: {{token0: "{token0Address}",   token1:"{token1Address}"}}) {{
        id
      }}
    }}
  }}""".format(token0Address = token0Address.lower(), token1Address = token1Address.lower())
    # endpoint where you are making the request - ON POLYGON
    request = requests.post(f'{api}'
                              '',
                              json={'query': queryK})
    if request.status_code == 200:
      tokenRequest = request.json()
      for eachElement in tokenRequest.values():
        if eachElement['token'] != None:
          if len(eachElement['token']['whitelistPools']) > 1:
            poolAddress = eachElement['token']['whitelistPools'][0]['id']
            exchanges_address = {
              'KYBERSWAP': str(poolAddress)
            }
            tokens_address = {
              'WETH': str(token0Address),
              'DAI': str(token1Address)
            }
            return tokens_address, exchanges_address
    else:
      raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, queryK))
    

tokenDict, exchangeDict = getExchangePool_K(aDicOfToken)

arbObject = arbitrage.ArbitrageAPI(
  tokenAddress = tokenDict,
  exchangeAddress = exchangeDict
  )

main.run_menu(arbObject)
