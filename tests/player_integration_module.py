"""
LINE Bot用学習済み選手情報統合モジュール
"""

import json
import re
from typing import Dict, List, Optional

class PlayerInfoHandler:
    """選手情報ハンドラー"""

    def __init__(self):
        # 学習済み選手データ（埋め込み）
        self.player_list = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新",
            "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美"
        ]

        self.total_players = 13
        self.team_name = "馬三ソフト"

        # 基本応答テンプレート
        self.templates = {
            'team_overview': f"{self.team_name}には{self.total_players}名の選手が参加しています。選手一覧: {', '.join(self.player_list)}。どの選手について詳しく知りたいですか？",
            'player_count': f"{self.team_name}の参加選手は{self.total_players}名です。",
            'player_list': f"参加選手一覧: {', '.join(self.player_list)}",
            'unknown_player': f"申し訳ございませんが、その選手は{self.team_name}の参加選手リストにはいません。参加選手は: {', '.join(self.player_list)} です。"
        }

    def find_player_in_message(self, message: str) -> Optional[str]:
        """メッセージから選手名を検出"""
        for player in self.player_list:
            # 直接マッチ
            if player in message:
                return player

            # パターンマッチ
            patterns = [
                f'{player}選手',
                f'{player}君',
                f'{player}さん',
                f'{player}について',
                f'{player}の',
                f'{player}は',
                f'{player}が'
            ]

            for pattern in patterns:
                if pattern in message:
                    return player

        return None

    def get_player_response(self, player_name: str, message: str) -> str:
        """選手に関する応答生成"""
        player_index = self.player_list.index(player_name) + 1

        if '詳しく' in message or '詳細' in message:
            return f"{player_name}選手（{player_index}番）は{self.team_name}の大切なメンバーです。どのようなことをお知りになりたいですか？"
        elif '読み方' in message or '読み' in message:
            return f"{player_name}選手の読み方についてお答えします。"
        elif '何' in message or '？' in message or '?' in message:
            return f"{player_name}選手について何をお知りになりたいですか？"
        else:
            return f"{player_name}選手についてお答えします。{player_name}選手は{self.team_name}の{player_index}番目に登録された選手です。"

    def get_team_response(self, message: str) -> str:
        """チーム全体に関する応答"""
        if '一覧' in message or 'リスト' in message:
            return self.templates['player_list']
        elif '何人' in message or '人数' in message:
            return self.templates['player_count']
        else:
            return self.templates['team_overview']

    def handle_message(self, message: str) -> Optional[str]:
        """メッセージハンドリング"""
        # 選手名検出
        detected_player = self.find_player_in_message(message)

        if detected_player:
            return self.get_player_response(detected_player, message)

        # チーム全体への質問かチェック
        team_keywords = ['選手', 'チーム', '馬三ソフト', 'メンバー', '参加者']
        if any(keyword in message for keyword in team_keywords):
            return self.get_team_response(message)

        return None

    def get_all_players(self) -> List[str]:
        """全選手リスト取得"""
        return self.player_list.copy()

    def get_player_count(self) -> int:
        """選手数取得"""
        return self.total_players

    def is_valid_player(self, player_name: str) -> bool:
        """有効な選手名かチェック"""
        return player_name in self.player_list

# グローバルインスタンス
player_handler = PlayerInfoHandler()

def handle_player_query(message: str) -> Optional[str]:
    """選手クエリハンドリング関数（外部から使用）"""
    return player_handler.handle_message(message)
