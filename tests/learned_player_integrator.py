"""
学習済み選手情報をLINE Botに統合するシステム
"""

import json
import os
import re
from typing import Dict, List, Optional

class LearnedPlayerIntegrator:
    """学習済み選手情報統合システム"""

    def __init__(self):
        # 学習データファイルパス
        self.player_db_path = 'learned_player_database.json'
        self.templates_path = 'player_response_templates.json'
        self.search_system_path = 'player_search_system.json'

        # 学習データロード
        self.player_database = self.load_player_database()
        self.response_templates = self.load_response_templates()
        self.search_system = self.load_search_system()

    def load_player_database(self) -> Dict:
        """選手データベースロード"""
        try:
            with open(self.player_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 選手データベースが見つかりません: {self.player_db_path}")
            return {}

    def load_response_templates(self) -> Dict:
        """応答テンプレートロード"""
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 応答テンプレートが見つかりません: {self.templates_path}")
            return {}

    def load_search_system(self) -> Dict:
        """検索システムロード"""
        try:
            with open(self.search_system_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 検索システムが見つかりません: {self.search_system_path}")
            return {}

    def find_player_in_message(self, message: str) -> Optional[str]:
        """メッセージから選手名を検出"""
        if not self.player_database or 'players' not in self.player_database:
            return None

        # 各選手名をチェック
        for player_info in self.player_database['players']:
            player_name = player_info['name']

            # 直接マッチ
            if player_name in message:
                return player_name

            # パターンマッチ
            patterns = [
                f'{player_name}選手',
                f'{player_name}君',
                f'{player_name}さん',
                f'{player_name}について',
                f'{player_name}の',
                f'{player_name}は',
                f'{player_name}が'
            ]

            for pattern in patterns:
                if pattern in message:
                    return player_name

        return None

    def get_player_response(self, player_name: str, message: str) -> str:
        """選手に関する応答生成"""
        if not self.response_templates:
            return f"{player_name}選手についてお答えします。"

        # メッセージの内容に応じてテンプレート選択
        if '詳しく' in message or '詳細' in message:
            template_key = f'{player_name}_detail'
        elif '読み方' in message or '読み' in message:
            template_key = f'{player_name}_reading'
        elif '何' in message or '？' in message or '?' in message:
            template_key = f'{player_name}_question'
        else:
            template_key = f'{player_name}_basic'

        # テンプレートが存在すれば使用、なければ基本応答
        if template_key in self.response_templates:
            return self.response_templates[template_key]
        elif f'{player_name}_basic' in self.response_templates:
            return self.response_templates[f'{player_name}_basic']
        else:
            return f"{player_name}選手についてお答えします。馬三ソフトの大切なメンバーです。"

    def get_team_overview_response(self, message: str) -> str:
        """チーム全体に関する応答"""
        if not self.response_templates:
            return "馬三ソフトの選手について お答えします。"

        if '一覧' in message or 'リスト' in message:
            return self.response_templates.get('player_list', '選手一覧をお答えします。')
        elif '何人' in message or '人数' in message:
            return self.response_templates.get('player_count', '選手数についてお答えします。')
        else:
            return self.response_templates.get('team_overview', 'チームについてお答えします。')

    def handle_player_query(self, message: str) -> Optional[str]:
        """選手関連クエリのハンドリング"""
        # 選手名検出
        detected_player = self.find_player_in_message(message)

        if detected_player:
            return self.get_player_response(detected_player, message)

        # チーム全体への質問かチェック
        team_keywords = ['選手', 'チーム', '馬三ソフト', 'メンバー', '参加者']
        if any(keyword in message for keyword in team_keywords):
            return self.get_team_overview_response(message)

        return None

    def create_integration_module(self):
        """統合モジュール作成"""
        integration_code = '''"""
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
'''

        # 統合モジュール保存
        module_path = 'player_integration_module.py'
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(integration_code)

        print(f"✅ 統合モジュール作成: {module_path}")
        return module_path

    def update_uma3_bot(self):
        """uma3.pyに選手情報統合を追加"""
        uma3_path = os.path.join('..', 'src', 'uma3.py')

        if not os.path.exists(uma3_path):
            print(f"⚠️ uma3.pyが見つかりません: {uma3_path}")
            return False

        # uma3.pyの現在の内容を読み取り
        try:
            with open(uma3_path, 'r', encoding='utf-8') as f:
                current_code = f.read()

            # 既に選手情報統合が追加されているかチェック
            if 'PlayerInfoHandler' in current_code:
                print("ℹ️ uma3.pyには既に選手情報統合が追加されています")
                return True

            # 選手情報統合コードを追加
            integration_import = '''
# 学習済み選手情報統合
from typing import Optional

class PlayerInfoHandler:
    """選手情報ハンドラー"""

    def __init__(self):
        self.player_list = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新",
            "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美"
        ]
        self.total_players = 13
        self.team_name = "馬三ソフト"

    def find_player_in_message(self, message: str) -> Optional[str]:
        """メッセージから選手名を検出"""
        for player in self.player_list:
            if player in message or f'{player}選手' in message or f'{player}君' in message:
                return player
        return None

    def handle_message(self, message: str) -> Optional[str]:
        """選手関連メッセージハンドリング"""
        detected_player = self.find_player_in_message(message)

        if detected_player:
            player_index = self.player_list.index(detected_player) + 1
            return f"{detected_player}選手についてお答えします。{detected_player}選手は{self.team_name}の{player_index}番目に登録された選手です。"

        # チーム全体への質問
        team_keywords = ['選手', 'チーム', '馬三ソフト', 'メンバー', '参加者']
        if any(keyword in message for keyword in team_keywords):
            if '一覧' in message or 'リスト' in message:
                return f"参加選手一覧: {', '.join(self.player_list)}"
            elif '何人' in message or '人数' in message:
                return f"{self.team_name}の参加選手は{self.total_players}名です。"
            else:
                return f"{self.team_name}には{self.total_players}名の選手が参加しています。選手一覧: {', '.join(self.player_list)}。どの選手について詳しく知りたいですか？"

        return None

# グローバル選手情報ハンドラー
player_info_handler = PlayerInfoHandler()
'''

            # インポート文の後に統合コードを挿入
            import_end = current_code.find('\n\n')
            if import_end != -1:
                updated_code = current_code[:import_end] + integration_import + current_code[import_end:]
            else:
                updated_code = integration_import + '\n\n' + current_code

            # バックアップ作成
            backup_path = uma3_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(current_code)

            print(f"💾 バックアップ作成: {backup_path}")

            # 更新されたコードを保存
            with open(uma3_path, 'w', encoding='utf-8') as f:
                f.write(updated_code)

            print(f"✅ uma3.py更新完了")
            return True

        except Exception as e:
            print(f"❌ uma3.py更新エラー: {e}")
            return False

    def create_test_script(self):
        """テストスクリプト作成"""
        test_code = '''"""
選手情報統合テストスクリプト
"""

import sys
import os

# player_integration_moduleをインポート
try:
    from player_integration_module import handle_player_query
    print("✅ 選手情報モジュール読み込み成功")
except ImportError as e:
    print(f"❌ モジュール読み込みエラー: {e}")
    sys.exit(1)

def test_player_queries():
    """選手クエリテスト"""
    print("🧪 選手クエリテスト開始")
    print("=" * 40)

    test_messages = [
        "陸功選手について教えて",
        "湊君はどんな選手？",
        "錬について詳しく知りたい",
        "南選手の読み方は？",
        "統司について",
        "春輝選手",
        "新君のこと教えて",
        "由眞選手について詳細を",
        "心寧について何か知ってる？",
        "唯浬選手",
        "朋樹君",
        "佑多選手は？",
        "穂美について",
        "選手一覧を教えて",
        "チームには何人いる？",
        "馬三ソフトのメンバーは？",
        "参加者リスト",
        "存在しない選手について"  # 存在しない選手
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"{i:2d}. 入力: {message}")
        response = handle_player_query(message)
        if response:
            print(f"    応答: {response}")
        else:
            print(f"    応答: （選手情報に該当なし）")
        print()

if __name__ == "__main__":
    test_player_queries()
'''

        test_path = 'test_player_integration.py'
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_code)

        print(f"✅ テストスクリプト作成: {test_path}")
        return test_path

def main():
    """メイン処理"""
    print("🔗 学習済み選手情報統合システム")
    print("=" * 50)

    # 統合システム初期化
    integrator = LearnedPlayerIntegrator()

    if not integrator.player_database:
        print("❌ 選手データベースが読み込めません。先に学習システムを実行してください。")
        return

    print(f"✅ 学習データ読み込み完了")
    print(f"   - 選手数: {integrator.player_database.get('team_info', {}).get('total_players', 0)}名")
    print(f"   - テンプレート数: {len(integrator.response_templates)}")

    # 1. 統合モジュール作成
    module_path = integrator.create_integration_module()

    # 2. uma3.py更新
    uma3_updated = integrator.update_uma3_bot()

    # 3. テストスクリプト作成
    test_path = integrator.create_test_script()

    print(f"\n🎉 統合処理完了！")
    print(f"📁 作成ファイル:")
    print(f"   - {module_path}")
    print(f"   - {test_path}")

    if uma3_updated:
        print(f"   - uma3.py（更新済み）")
    else:
        print(f"   - uma3.py（更新失敗）")

if __name__ == "__main__":
    main()
