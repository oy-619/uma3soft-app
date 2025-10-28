
# 更新版拡張可能選手情報統合（一括学習対応）
class UpdatedExpandablePlayerInfoHandler:
    """更新版拡張可能選手情報ハンドラー"""

    def __init__(self):
        # 確認済み選手（更新版 - 28名）
        self.confirmed_players = ['陸功', '湊', '錬', '南', '統司', '春輝', '新', '由眞', '心寧', '唯浬', '朋樹', '佑多', '穂美', '翔平', '尚真', '柚希', '心翔', '広起', '想真', '奏', '英汰', '聡太', '暖大', '悠琉', '陽', '美玖里', '優', '勘太']

        # 候補選手（更新版 - 0名）
        self.potential_players = []

        # 全選手
        self.all_players = self.confirmed_players + self.potential_players
        self.total_players = len(self.all_players)
        self.team_name = "馬三ソフト"

        # 学習・更新機能
        self.expandable = True
        self.can_learn_new_players = True
        self.batch_learning_supported = True

        # 一括更新情報
        self.last_batch_update = "2025-10-28T08:56:42.887268"
        self.batch_update_count = 16

    def find_player_in_message(self, message: str) -> Optional[str]:
        """メッセージから選手名を検出（更新版）"""
        for player in self.all_players:
            # 直接マッチング
            patterns = [
                player,
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

    def get_player_status(self, player_name: str) -> str:
        """選手のステータス取得"""
        if player_name in self.confirmed_players:
            return 'confirmed'
        elif player_name in self.potential_players:
            return 'potential'
        else:
            return 'unknown'

    def handle_message(self, message: str) -> Optional[str]:
        """メッセージハンドリング（更新版）"""
        detected_player = self.find_player_in_message(message)

        if detected_player:
            status = self.get_player_status(detected_player)
            player_index = self.all_players.index(detected_player) + 1

            if status == 'confirmed':
                # 翔平の特別処理
                if detected_player == "翔平":
                    return f"{detected_player}選手についてお答えします。{detected_player}選手は{self.team_name}の確認済み選手として新たに正式登録されました。"
                else:
                    return f"{detected_player}選手についてお答えします。{detected_player}選手は{self.team_name}の確認済み選手で、{player_index}番目に登録されています。"
            elif status == 'potential':
                return f"{detected_player}選手についてお答えします。{detected_player}選手は分析により発見された{self.team_name}のメンバーの可能性があります。詳細情報をお持ちでしたら教えてください。"

        # チーム全体への質問
        team_keywords = ['選手', 'チーム', '馬三ソフト', 'メンバー', '参加者']
        if any(keyword in message for keyword in team_keywords):
            if '一覧' in message or 'リスト' in message:
                confirmed_list = ', '.join(self.confirmed_players)
                if self.potential_players:
                    potential_list = ', '.join(self.potential_players)
                    return f"選手一覧：\n確認済み選手（{len(self.confirmed_players)}名）: {confirmed_list}\n候補選手（{len(self.potential_players)}名）: {potential_list}"
                else:
                    return f"確認済み選手一覧（{len(self.confirmed_players)}名）: {confirmed_list}"
            elif '何人' in message or '人数' in message:
                return f"{self.team_name}の現在の選手情報は{self.total_players}名です（確認済み{len(self.confirmed_players)}名、候補{len(self.potential_players)}名）。"
            elif '更新' in message or '新しい' in message:
                return f"最新の一括更新で{self.batch_update_count}名の選手情報をいただき、システムに統合いたしました。現在{self.total_players}名の選手情報があります。"
            else:
                return f"{self.team_name}には現在{self.total_players}名の選手情報があります。確認済み{len(self.confirmed_players)}名、候補{len(self.potential_players)}名です。どの選手について詳しく知りたいですか？"

        return None

# グローバル更新版拡張選手情報ハンドラー
updated_expandable_player_handler = UpdatedExpandablePlayerInfoHandler()
