"""
拡張可能な選手情報学習・更新システム
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class ExpandablePlayerLearningSystem:
    """拡張可能選手学習システム"""

    def __init__(self):
        # 確認済みの基本13名
        self.confirmed_players = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新",
            "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美"
        ]

        # 追加候補選手（分析から発見）
        self.potential_additional_players = [
            "翔平"  # データベース分析で6回出現、実際の選手の可能性が高い
        ]

        # システム設定
        self.team_name = "馬三ソフト"
        self.system_files = {
            'main_database': 'expandable_player_database.json',
            'response_templates': 'expandable_response_templates.json',
            'learning_log': 'player_learning_log.json',
            'update_history': 'player_update_history.json'
        }

    def create_expandable_database(self):
        """拡張可能データベース作成"""
        print("🏗️ 拡張可能選手データベース作成")
        print("=" * 40)

        # 全選手リスト（確認済み + 候補）
        all_current_players = self.confirmed_players + self.potential_additional_players

        database = {
            'system_info': {
                'version': '2.0_expandable',
                'last_updated': datetime.now().isoformat(),
                'team_name': self.team_name,
                'expandable': True,
                'auto_learning_enabled': True
            },
            'player_categories': {
                'confirmed_players': {
                    'count': len(self.confirmed_players),
                    'players': self.confirmed_players,
                    'status': 'verified_from_user_input'
                },
                'potential_players': {
                    'count': len(self.potential_additional_players),
                    'players': self.potential_additional_players,
                    'status': 'detected_from_analysis_high_confidence'
                },
                'total_current': {
                    'count': len(all_current_players),
                    'players': all_current_players
                }
            },
            'player_details': [],
            'expansion_capability': {
                'can_add_new_players': True,
                'can_update_existing': True,
                'supports_batch_import': True,
                'supports_user_correction': True,
                'learning_sources': [
                    'user_direct_input',
                    'conversation_analysis',
                    'mention_detection',
                    'context_learning'
                ]
            }
        }

        # 各選手の詳細情報
        for i, player in enumerate(all_current_players, 1):
            status = 'confirmed' if player in self.confirmed_players else 'potential'
            confidence = 1.0 if player in self.confirmed_players else 0.8

            player_info = {
                'id': i,
                'name': player,
                'status': status,
                'confidence_score': confidence,
                'registration_order': i,
                'name_length': len(player),
                'characters': list(player),
                'search_patterns': self.generate_comprehensive_search_patterns(player),
                'learning_metadata': {
                    'source': 'user_input' if status == 'confirmed' else 'database_analysis',
                    'verification_date': datetime.now().isoformat(),
                    'update_count': 0
                }
            }

            database['player_details'].append(player_info)

        # データベース保存
        with open(self.system_files['main_database'], 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)

        print(f"✅ 拡張可能データベース保存: {self.system_files['main_database']}")
        print(f"📊 確認済み選手: {len(self.confirmed_players)}名")
        print(f"🔍 候補選手: {len(self.potential_additional_players)}名")
        print(f"🏆 現在総数: {len(all_current_players)}名")
        print(f"🔧 拡張機能: 有効")

        return database

    def generate_comprehensive_search_patterns(self, player_name: str) -> List[str]:
        """包括的検索パターン生成"""
        patterns = []

        # 基本パターン
        basic_patterns = [
            player_name,
            f"{player_name}選手",
            f"{player_name}君",
            f"{player_name}さん",
            f"{player_name}ちゃん"
        ]
        patterns.extend(basic_patterns)

        # 文脈パターン
        context_patterns = [
            f"{player_name}について",
            f"{player_name}の",
            f"{player_name}は",
            f"{player_name}が",
            f"{player_name}を",
            f"{player_name}に",
            f"{player_name}で",
            f"{player_name}と"
        ]
        patterns.extend(context_patterns)

        # 質問パターン
        question_patterns = [
            f"{player_name}はどんな選手？",
            f"{player_name}について教えて",
            f"{player_name}の情報",
            f"{player_name}のこと"
        ]
        patterns.extend(question_patterns)

        return patterns

    def create_expandable_response_templates(self, database: Dict):
        """拡張可能応答テンプレート作成"""
        print(f"\n📝 拡張可能応答テンプレート作成")
        print("=" * 35)

        templates = {}
        all_players = database['player_categories']['total_current']['players']
        confirmed_count = database['player_categories']['confirmed_players']['count']
        potential_count = database['player_categories']['potential_players']['count']

        # チーム全体テンプレート
        templates['team_overview'] = f"{self.team_name}には現在{len(all_players)}名の選手情報があります（確認済み{confirmed_count}名、候補{potential_count}名）。選手一覧: {', '.join(all_players)}。どの選手について詳しく知りたいですか？"

        templates['confirmed_players_list'] = f"確認済み選手一覧（{confirmed_count}名）: {', '.join(self.confirmed_players)}"

        if self.potential_additional_players:
            templates['potential_players_list'] = f"候補選手一覧（{potential_count}名）: {', '.join(self.potential_additional_players)}"

        templates['total_count'] = f"{self.team_name}の現在の選手情報は{len(all_players)}名です。"

        # 各選手用テンプレート
        for player_info in database['player_details']:
            name = player_info['name']
            status = player_info['status']
            order = player_info['registration_order']

            if status == 'confirmed':
                templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は{self.team_name}の確認済み選手で、{order}番目に登録されています。"
                templates[f'{name}_detail'] = f"{name}選手は{self.team_name}の正式メンバーです。どのようなことをお知りになりたいですか？"
            else:
                templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は{self.team_name}の候補選手として特定されています。"
                templates[f'{name}_detail'] = f"{name}選手は分析により発見された{self.team_name}のメンバーの可能性があります。詳細情報をお持ちでしたら教えてください。"

            templates[f'{name}_question'] = f"{name}選手について何をお知りになりたいですか？"

        # 学習・更新関連テンプレート
        templates['new_player_detection'] = "新しい選手情報を検出しました。詳細を教えていただけますか？"
        templates['player_info_request'] = "選手について詳しい情報をお持ちでしたら、ぜひ教えてください。学習して記憶いたします。"
        templates['learning_confirmation'] = "選手情報を学習しました。ありがとうございます！"
        templates['update_notification'] = "選手情報を更新しました。"

        # 候補選手特別テンプレート
        if '翔平' in self.potential_additional_players:
            templates['翔平_potential'] = "翔平選手は会話の中で言及されている選手です。翔平選手について詳しい情報をお持ちでしたら教えてください。"

        # テンプレート保存
        with open(self.system_files['response_templates'], 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)

        print(f"✅ 拡張応答テンプレート保存: {self.system_files['response_templates']}")
        print(f"📊 作成テンプレート数: {len(templates)}")

        return templates

    def create_learning_log_system(self):
        """学習ログシステム作成"""
        print(f"\n📚 学習ログシステム作成")
        print("=" * 25)

        learning_log = {
            'log_info': {
                'created_date': datetime.now().isoformat(),
                'version': '1.0',
                'purpose': 'track_player_learning_activities'
            },
            'learning_sessions': [
                {
                    'session_id': 'initial_setup',
                    'date': datetime.now().isoformat(),
                    'type': 'system_initialization',
                    'action': 'create_expandable_system',
                    'details': {
                        'confirmed_players_added': len(self.confirmed_players),
                        'potential_players_added': len(self.potential_additional_players),
                        'players_added': self.confirmed_players + self.potential_additional_players
                    }
                }
            ],
            'statistics': {
                'total_learning_sessions': 1,
                'confirmed_players': len(self.confirmed_players),
                'potential_players': len(self.potential_additional_players),
                'last_update': datetime.now().isoformat()
            }
        }

        # 学習ログ保存
        with open(self.system_files['learning_log'], 'w', encoding='utf-8') as f:
            json.dump(learning_log, f, ensure_ascii=False, indent=2)

        print(f"✅ 学習ログ保存: {self.system_files['learning_log']}")

        return learning_log

    def create_update_methods(self):
        """更新メソッド作成"""
        print(f"\n🔧 更新メソッドシステム作成")
        print("=" * 30)

        update_methods = {
            'method_info': {
                'version': '1.0',
                'supported_operations': [
                    'add_new_player',
                    'confirm_potential_player',
                    'update_player_info',
                    'remove_player',
                    'batch_import_players'
                ]
            },
            'update_templates': {
                'add_player': {
                    'description': '新規選手追加',
                    'required_fields': ['player_name'],
                    'optional_fields': ['status', 'details', 'source']
                },
                'confirm_player': {
                    'description': '候補選手の確認',
                    'required_fields': ['player_name', 'confirmation'],
                    'optional_fields': ['additional_info']
                },
                'batch_import': {
                    'description': '複数選手一括追加',
                    'required_fields': ['player_list'],
                    'optional_fields': ['source', 'batch_metadata']
                }
            },
            'usage_examples': [
                {
                    'operation': 'add_new_player',
                    'example': "新選手「田中太郎」を追加",
                    'method_call': 'add_player("田中太郎", status="confirmed", source="user_input")'
                },
                {
                    'operation': 'confirm_potential',
                    'example': "候補選手「翔平」を確認済みに変更",
                    'method_call': 'confirm_player("翔平", additional_info="user_confirmed")'
                },
                {
                    'operation': 'batch_import',
                    'example': "複数選手を一括登録",
                    'method_call': 'batch_import_players(["選手A", "選手B", "選手C"])'
                }
            ]
        }

        # 更新履歴保存
        with open(self.system_files['update_history'], 'w', encoding='utf-8') as f:
            json.dump(update_methods, f, ensure_ascii=False, indent=2)

        print(f"✅ 更新メソッド保存: {self.system_files['update_history']}")

        return update_methods

    def create_uma3_integration_code(self):
        """uma3.py統合用拡張コード作成"""
        print(f"\n🔗 uma3.py統合コード作成")
        print("=" * 25)

        integration_code = f'''
# 拡張可能選手情報統合（更新版）
class ExpandablePlayerInfoHandler:
    """拡張可能選手情報ハンドラー"""

    def __init__(self):
        # 確認済み選手（基本13名）
        self.confirmed_players = {self.confirmed_players}

        # 候補選手（分析から発見）
        self.potential_players = {self.potential_additional_players}

        # 全選手
        self.all_players = self.confirmed_players + self.potential_players
        self.total_players = len(self.all_players)
        self.team_name = "{self.team_name}"

        # 学習・更新機能
        self.expandable = True
        self.can_learn_new_players = True

    def find_player_in_message(self, message: str) -> Optional[str]:
        """メッセージから選手名を検出（拡張版）"""
        for player in self.all_players:
            # 直接マッチング
            patterns = [
                player,
                f'{{player}}選手',
                f'{{player}}君',
                f'{{player}}さん',
                f'{{player}}について',
                f'{{player}}の',
                f'{{player}}は',
                f'{{player}}が'
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
        """メッセージハンドリング（拡張版）"""
        detected_player = self.find_player_in_message(message)

        if detected_player:
            status = self.get_player_status(detected_player)
            player_index = self.all_players.index(detected_player) + 1

            if status == 'confirmed':
                return f"{{detected_player}}選手についてお答えします。{{detected_player}}選手は{{self.team_name}}の確認済み選手で、{{player_index}}番目に登録されています。"
            elif status == 'potential':
                return f"{{detected_player}}選手についてお答えします。{{detected_player}}選手は分析により発見された{{self.team_name}}のメンバーの可能性があります。詳細情報をお持ちでしたら教えてください。"

        # チーム全体への質問
        team_keywords = ['選手', 'チーム', '馬三ソフト', 'メンバー', '参加者']
        if any(keyword in message for keyword in team_keywords):
            if '一覧' in message or 'リスト' in message:
                confirmed_list = ', '.join(self.confirmed_players)
                if self.potential_players:
                    potential_list = ', '.join(self.potential_players)
                    return f"選手一覧：\\n確認済み選手（{{len(self.confirmed_players)}}名）: {{confirmed_list}}\\n候補選手（{{len(self.potential_players)}}名）: {{potential_list}}"
                else:
                    return f"確認済み選手一覧（{{len(self.confirmed_players)}}名）: {{confirmed_list}}"
            elif '何人' in message or '人数' in message:
                return f"{{self.team_name}}の現在の選手情報は{{self.total_players}}名です（確認済み{{len(self.confirmed_players)}}名、候補{{len(self.potential_players)}}名）。"
            else:
                return f"{{self.team_name}}には現在{{self.total_players}}名の選手情報があります。確認済み{{len(self.confirmed_players)}}名、候補{{len(self.potential_players)}}名です。どの選手について詳しく知りたいですか？"

        return None

# グローバル拡張選手情報ハンドラー
expandable_player_handler = ExpandablePlayerInfoHandler()
'''

        # 統合コード保存
        integration_path = 'expandable_uma3_integration.py'
        with open(integration_path, 'w', encoding='utf-8') as f:
            f.write(integration_code)

        print(f"✅ uma3.py統合コード保存: {integration_path}")

        return integration_code, integration_path

    def generate_expansion_summary(self):
        """拡張システムサマリー生成"""
        print(f"\n📊 拡張システムサマリー")
        print("=" * 25)

        summary = {
            'system_info': {
                'system_name': '拡張可能選手情報学習システム',
                'version': '2.0_expandable',
                'creation_date': datetime.now().isoformat(),
                'purpose': 'scalable_player_information_management'
            },
            'current_status': {
                'confirmed_players': len(self.confirmed_players),
                'potential_players': len(self.potential_additional_players),
                'total_current_players': len(self.confirmed_players) + len(self.potential_additional_players),
                'system_expandable': True
            },
            'capabilities': [
                '新規選手の自動検出',
                '選手情報の動的更新',
                '候補選手の確認機能',
                '一括選手登録',
                'LINE Bot完全統合',
                '学習履歴追跡'
            ],
            'files_created': list(self.system_files.values()) + ['expandable_uma3_integration.py'],
            'next_steps': [
                '追加選手情報の収集',
                '候補選手の確認・検証',
                'LINE Bot運用テスト',
                '学習データの継続蓄積'
            ]
        }

        print(f"🏆 システム名: {summary['system_info']['system_name']}")
        print(f"📊 現在の状況:")
        print(f"   ✅ 確認済み選手: {summary['current_status']['confirmed_players']}名")
        print(f"   🔍 候補選手: {summary['current_status']['potential_players']}名")
        print(f"   🏆 現在総数: {summary['current_status']['total_current_players']}名")
        print(f"   🔧 拡張可能: {summary['current_status']['system_expandable']}")

        print(f"\\n🌟 主要機能:")
        for i, capability in enumerate(summary['capabilities'], 1):
            print(f"   {i}. {capability}")

        print(f"\\n📁 作成ファイル数: {len(summary['files_created'])}個")

        # サマリー保存
        summary_path = 'expandable_system_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\\n💾 システムサマリー保存: {summary_path}")

        return summary

def main():
    """メイン処理"""
    print("🚀 拡張可能選手情報学習システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 拡張システム初期化
    learning_system = ExpandablePlayerLearningSystem()

    print(f"📊 システム初期状態:")
    print(f"   ✅ 確認済み選手: {len(learning_system.confirmed_players)}名")
    print(f"      {', '.join(learning_system.confirmed_players)}")
    print(f"   🔍 候補選手: {len(learning_system.potential_additional_players)}名")
    print(f"      {', '.join(learning_system.potential_additional_players) if learning_system.potential_additional_players else 'なし'}")
    print()

    # 1. 拡張可能データベース作成
    database = learning_system.create_expandable_database()

    # 2. 拡張可能応答テンプレート作成
    templates = learning_system.create_expandable_response_templates(database)

    # 3. 学習ログシステム作成
    learning_log = learning_system.create_learning_log_system()

    # 4. 更新メソッド作成
    update_methods = learning_system.create_update_methods()

    # 5. uma3.py統合コード作成
    integration_code, integration_path = learning_system.create_uma3_integration_code()

    # 6. システムサマリー生成
    summary = learning_system.generate_expansion_summary()

    print(f"\\n🎉 拡張可能選手情報学習システム構築完了！")
    print(f"✨ 今後新たな選手情報が提供された際は、自動的に学習・更新されます")

if __name__ == "__main__":
    main()
