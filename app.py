"""Crypto Interview Assessment Module."""

from dotenv import find_dotenv, load_dotenv
import crypto_api
from typing import Dict, List
from models import CoinHistory, DBSession
from apscheduler.schedulers.blocking import BlockingScheduler
from logger import Logger

load_dotenv(find_dotenv(raise_error_if_not_found=True))

class CryptoTrading:

    def __init__(self):
        self.__top_n_coins = 3
        self.__past_x_days = 10
        self.__order_qty = 1
        self.__db_session = DBSession().create_db_session()
        self.__logger = Logger()

    def __get_coin_data(self) -> List[Dict]:
        """Gets coin prices for top_n_coins by market cap"""
        coins = crypto_api.get_coins()
        n = self.__top_n_coins
        top_n_coins = []
        for i in range(n):
            coin = coins[i]
            top_n_coins.append({'id': coin['id'], 
                                'symbol': coin['symbol'], 
                                'name': coin['name'], 
                                'price': coin['current_price']})
        return top_n_coins

    def __get_coin_price(self, coin_id: str) -> float:
        """Gets the avg price of coin_id averaged over past_x_days"""
        coin_prices = crypto_api.get_coin_price_history(coin_id=coin_id)
        x_days = self.__past_x_days
        sum_price = 0
        for price in coin_prices:
            sum_price += price[1]
        avg_price = sum_price / x_days
        return avg_price

    def __place_order(self, coin_id: str, quantity: int, price: float) -> bool:
        """Places an order for coin_id at price for quantity no. of coins"""
        bid_price = crypto_api.submit_order(coin_id=coin_id, quantity=quantity, bid=price)
        return bid_price

    def __save_coin_to_db(self, coin: CoinHistory) -> bool:
        """Saves coin object to database"""
        self.__db_session.add(coin)
        self.__db_session.commit()
        return True

    def __get_portfolio(self, top_3_coins):
        """Gets the total portfolio of coins owned"""
        ##TODO: Cache the current results so that next time computation will be on top of current results
        query = "SELECT symbol, SUM(quantity), AVG(price) FROM crypto.coin_history WHERE bought=1 GROUP BY symbol;"
        portfolio = self.__db_session.execute(query)
        computed_portfolio = []
        for position in portfolio:
            symbol = position[0]
            quantity = int(position[1])
            avg_buy_price = position[2]
            pct_profit = 0
            for coin in top_3_coins:
                if position[0] == coin['symbol']:
                    pct_profit = (coin['price'] - avg_buy_price) / avg_buy_price
                    pct_profit = round(pct_profit * 100, 2)
            computed_portfolio.append((symbol, quantity, round(avg_buy_price, 3), pct_profit))
        self.__logger.log('***********Current Portfolio***********')
        #self.__logger.log('(Symbol | Qty Bought | Avg Buy Price | Pct Profit)')
        for comp_position in computed_portfolio:
            self.__logger.log(f"Bought {comp_position[1]} coin/s of {comp_position[0]} at average price of {comp_position[2]}, percentage profit made {comp_position[3]}")
        self.__logger.log('***************************************')

    def crypto_trader(self):
        """Trading module, places trades as per rules"""
        #get top 3 coins by market cap
        top_3_coins = self.__get_coin_data()
        for coin in top_3_coins:
            bought=False
            #get avg price of coin over last 10 days
            avg_price = self.__get_coin_price(coin_id = coin['id'])
            curr_price = coin['price']
            if curr_price < avg_price:
                #place order for 1 coin since current price < average price
                bid_price = self.__place_order(coin_id=coin['id'], quantity=quantity, price=curr_price)
                bought = True
                quantity = self.__order_qty
                #log the trade
                self.__logger.log(f"Trade made for {coin['name']} at {bid_price}, bought {quantity} coin/s")
            else:
                quantity = 0
                bid_price=curr_price
            #create a coin obj and save to db
            coin_obj = CoinHistory().create_coin(symbol=coin['symbol'],
                                                name=coin['name'],
                                                price=bid_price,
                                                bought=bought,
                                                quantity=quantity)
            if self.__save_coin_to_db(coin_obj):
                self.__logger.log(msg=f"Successfully saved {coin['name']} to db", console=False)
        #log the current portfolio
        self.__get_portfolio(top_3_coins)
            
            
if __name__ == '__main__':
    scheduler = BlockingScheduler()
    cryptotrader = CryptoTrading()
    logger = Logger()

    @scheduler.scheduled_job('interval', minutes=60)
    def trader():
        cryptotrader.crypto_trader()

    logger.log('Hello! Welcome to crypto trading..')
    logger.log('At any point, press Ctrl+C to quit the application')
    trader()
    try:  
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.log('End of crypto trading for now.. Good bye!')
