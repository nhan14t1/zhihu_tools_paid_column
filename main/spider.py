import csv
import logging
import os
import random
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
import fakeUserAgent
import marketSpider


class zhihuSpider:
    BATCH_DELAY_MIN_SECONDS = 3
    BATCH_DELAY_MAX_SECONDS = 8

    def __init__(self) -> None:
        self.__config = config.Config().getEnviroments()
        self.__option = None
        self.__header = {}
        self.__header["Cookie"] = self.__config["Cookie"]
        self.__header["User-Agent"] = (
            self.__config["User-Agent"]
            + " "
            + str(fakeUserAgent.fakeUserAgent().getRandomUserAgent())
        )

    def getOptionChoise(self) -> str:
        if self.__option == "1":
            return self.optionChoise1()
        if self.__option == "2":
            return self.optionChoise2()
        if self.__option == "3":
            return self.optionChoise3()
        if self.__option == "4":
            return self.optionChoise4()
        if self.__option == "5":
            return self.optionChoise5()
        return self.commandChoise()

    def optionChoise1(self) -> str:
        logging.info("暂时不想开发。点个start鼓励鼓励作者让他开发吧！")
        logging.info("https://github.com/onewhitethreee/zhihu_tools")
        exit(0)

    def optionChoise2(self) -> str:
        logging.info("请输入你要解析的链接: ")
        link = input().strip()
        market = marketSpider.MarketSpider(self.__header)
        market.spider(link)
        return link

    def optionChoise3(self) -> str:
        logging.info("暂时不想开发。点个start鼓励鼓励作者让他开发吧！")
        logging.info("https://github.com/onewhitethreee/zhihu_tools")
        exit(0)

    def optionChoise4(self) -> str:
        logging.info("暂时不想开发。点个start鼓励鼓励作者让他开发吧！")
        logging.info("https://github.com/onewhitethreee/zhihu_tools")
        exit(0)

    def optionChoise5(self) -> str:
        csv_path = "urls.csv"
        output_dir = "output"

        if not os.path.exists(csv_path):
            logging.error("未找到 urls.csv 文件！")
            return ""

        os.makedirs(output_dir, exist_ok=True)
        processed_count = 0

        rows_to_process = []

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.reader(csv_file)
            for row_number, row in enumerate(reader, start=1):
                if not row or all(not cell.strip() for cell in row):
                    continue

                if len(row) < 2:
                    logging.warning(f"urls.csv 第 {row_number} 行格式无效，已跳过: {row}")
                    continue

                story_id = row[0].strip()
                link = row[1].strip()

                if not story_id or not link:
                    logging.warning(f"urls.csv 第 {row_number} 行缺少 ID 或 URL，已跳过: {row}")
                    continue

                rows_to_process.append((story_id, link))

        for index, (story_id, link) in enumerate(rows_to_process, start=1):
            logging.info(f"开始批量爬取: {story_id} -> {link}")
            market = marketSpider.MarketSpider(
                self.__header, output_dir=output_dir, filename_prefix=story_id
            )
            market.spider(link)
            processed_count += 1

            if index < len(rows_to_process):
                delay_seconds = random.uniform(
                    self.BATCH_DELAY_MIN_SECONDS, self.BATCH_DELAY_MAX_SECONDS
                )
                logging.info(f"等待 {delay_seconds:.2f} 秒后继续下一条，降低被限制风险。")
                time.sleep(delay_seconds)

        logging.info(f"批量爬取完成，共处理 {processed_count} 条链接。")
        return csv_path

    def commandChoise(self) -> str:
        return self.__option


if __name__ == "__main__":
    spider = zhihuSpider()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.info("=====================================")
    logging.info("程序启动")
    time.sleep(1)
    logging.info("=====================================")

    while 1:
        logging.info("请输入你的选项: ")
        logging.info("1. 爬取严选的单个问题")
        logging.info("2. 爬取书的单个章节")
        logging.info("3. 爬取整本书")
        logging.info("4. 关键词爬取")
        logging.info("5. 批量爬取 urls.csv")
        logging.info("0. 退出")
        spider._zhihuSpider__option = input()
        if spider._zhihuSpider__option == "0":
            break
        spider.getOptionChoise()
    logging.info("=====================================")
    logging.info("程序退出")
