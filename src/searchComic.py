from __future__ import annotations
from src.utils import logger

from PySide6.QtWidgets import QMessageBox

import requests
from retrying import retry, RetryError

import typing
if typing.TYPE_CHECKING:
    from ui.MainGUI import MainGUI

class SearchComic:
    """根据名字搜索漫画类
    """
    def __init__(self, comicName: str, sessdata: str) -> None:
        self.comicName = comicName
        self.sessdata = sessdata
        self.detailUrl = 'https://manga.bilibili.com/twirp/comic.v1.Comic/Search?device=pc&platform=web'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'origin': 'https://manga.bilibili.com',
            'referer': 'https://manga.bilibili.com/search?from=manga_homepage',
            'cookie': f'SESSDATA={sessdata}'
        }
        self.payload = {
            "key_word": comicName,
            "page_num": 1,
            "page_size": 99
        }

    ############################################################
    def getResults(self, mainGUI: MainGUI) -> list:
        """获取搜索结果

        Returns:
            list: 搜索结果列表
        """
        @retry(stop_max_delay=5000, wait_exponential_multiplier=200)
        def _() -> list:
            try:
                res = requests.post(self.detailUrl, data=self.payload, headers=self.headers, timeout=2)
            except requests.RequestException() as e:
                logger.warning(f"获取搜索结果失败! 重试中...\n{e}")
                raise e
            if res.status_code != 200:
                logger.warning(f"获取搜索结果失败! 状态码：{res.status_code}, 理由: {res.reason} 重试中...")
                raise requests.HTTPError()
            return res.json()['data']['list']

        logger.info(f"正在搜索漫画:《{self.comicName}》中...")

        try:
            data = _()
        except RetryError as e:
            logger.error(f'重复获取搜索结果多次后失败!\n{e}')
            QMessageBox.warning(mainGUI, "警告",  "重复获取搜索结果多次后失败!\n请检查网络连接或者重启软件!\n\n更多详细信息请查看日志文件")
            return []

        logger.info(f"搜索结果数量:{len(data)}")
        return data
