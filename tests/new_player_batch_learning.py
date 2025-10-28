"""
新規選手一括学習システム
提供された16名の選手を既存システムに統合
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class NewPlayerBatchLearning:
    """新規選手一括学習システム"""

    def __init__(self):
        # 既存の確認済み選手（13名）
        self.existing_confirmed_players = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新",
            "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美"
        ]

        # 既存の候補選手（1名）
        self.existing_potential_players = [
            "翔平"
        ]

        # 新規提供選手（16名）
        self.new_provided_players = [
            "尚真", "柚希", "穂美", "心翔", "広起", "想真", "奏", "英汰",
            "聡太", "暖大", "悠琉", "陽", "美玖里", "優", "翔平", "勘太"
        ]

        # システム設定
        self.team_name = "馬三ソフト"
        self.system_files = {
            'updated_database': 'updated_expandable_player_database.json',
            'updated_templates': 'updated_expandable_response_templates.json',
            'batch_learning_log': 'new_player_batch_learning_log.json',
            'integration_update': 'updated_uma3_integration.py'
        }

    def analyze_new_players(self):
        """新規選手の分析処理"""
        print("🔍 新規提供選手分析")
        print("=" * 30)

        # 重複チェック
        duplicates_with_existing = []
        truly_new_players = []

        all_existing = self.existing_confirmed_players + self.existing_potential_players

        for player in self.new_provided_players:
            if player in all_existing:
                duplicates_with_existing.append(player)
            else:
                truly_new_players.append(player)

        print(f"📊 分析結果:")
        print(f"   🆕 完全に新しい選手: {len(truly_new_players)}名")
        if truly_new_players:
            print(f"      {', '.join(truly_new_players)}")

        print(f"   🔄 既存選手との重複: {len(duplicates_with_existing)}名")
        if duplicates_with_existing:
            print(f"      {', '.join(duplicates_with_existing)}")

        # 「翔平」の状態変更分析
        if "翔平" in duplicates_with_existing:
            print(f"   ✅ 翔平: 候補選手 → 確認済み選手に昇格")

        # 「穂美」の重複分析
        if "穂美" in duplicates_with_existing:
            print(f"   ℹ️ 穂美: 既に確認済み選手として登録済み（重複確認）")

        return {
            'truly_new_players': truly_new_players,
            'duplicates': duplicates_with_existing,
            '翔平_status_change': "翔平" in duplicates_with_existing,
            '穂美_duplicate_confirmation': "穂美" in duplicates_with_existing
        }

    def create_updated_player_database(self, analysis_result: Dict):
        """更新された選手データベース作成"""
        print(f"\n🏗️ 更新選手データベース作成")
        print("=" * 35)

        # 最新の確認済み選手リスト作成
        updated_confirmed_players = self.existing_confirmed_players.copy()

        # 翔平を候補から確認済みに移動
        if analysis_result['翔平_status_change']:
            updated_confirmed_players.append("翔平")

        # 完全に新しい選手を確認済みに追加
        updated_confirmed_players.extend(analysis_result['truly_new_players'])

        # 候補選手リスト更新（翔平を除去）
        updated_potential_players = []
        for player in self.existing_potential_players:
            if player != "翔平":
                updated_potential_players.append(player)

        # 全選手リスト
        all_updated_players = updated_confirmed_players + updated_potential_players

        print(f"📈 更新後の構成:")
        print(f"   ✅ 確認済み選手: {len(updated_confirmed_players)}名")
        print(f"   🔍 候補選手: {len(updated_potential_players)}名")
        print(f"   🏆 総選手数: {len(all_updated_players)}名")

        # データベース構造作成
        updated_database = {
            'system_info': {
                'version': '3.0_batch_updated',
                'last_updated': datetime.now().isoformat(),
                'team_name': self.team_name,
                'expandable': True,
                'auto_learning_enabled': True,
                'batch_update_info': {
                    'update_date': datetime.now().isoformat(),
                    'new_players_added': len(analysis_result['truly_new_players']),
                    'status_changes': 1 if analysis_result['翔平_status_change'] else 0,
                    'duplicates_handled': len(analysis_result['duplicates'])
                }
            },
            'player_categories': {
                'confirmed_players': {
                    'count': len(updated_confirmed_players),
                    'players': updated_confirmed_players,
                    'status': 'verified_from_user_input'
                },
                'potential_players': {
                    'count': len(updated_potential_players),
                    'players': updated_potential_players,
                    'status': 'detected_from_analysis_high_confidence'
                },
                'total_current': {
                    'count': len(all_updated_players),
                    'players': all_updated_players
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
                    'context_learning',
                    'batch_import'
                ]
            },
            'batch_update_history': [
                {
                    'update_id': 'batch_001',
                    'date': datetime.now().isoformat(),
                    'type': 'user_provided_batch',
                    'players_added': analysis_result['truly_new_players'],
                    'status_changes': [
                        {'player': '翔平', 'from': 'potential', 'to': 'confirmed'}
                    ] if analysis_result['翔平_status_change'] else [],
                    'total_before': len(self.existing_confirmed_players) + len(self.existing_potential_players),
                    'total_after': len(all_updated_players)
                }
            ]
        }

        # 各選手の詳細情報作成
        for i, player in enumerate(all_updated_players, 1):
            status = 'confirmed' if player in updated_confirmed_players else 'potential'
            confidence = 1.0 if status == 'confirmed' else 0.8

            # 選手の情報源判定
            if player in self.existing_confirmed_players:
                source = 'initial_user_input'
            elif player == "翔平":
                source = 'promoted_from_potential'
            elif player in analysis_result['truly_new_players']:
                source = 'batch_user_input'
            else:
                source = 'database_analysis'

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
                    'source': source,
                    'verification_date': datetime.now().isoformat(),
                    'update_count': 1 if player == "翔平" else 0,
                    'batch_info': {
                        'batch_id': 'batch_001' if player in analysis_result['truly_new_players'] or player == "翔平" else None,
                        'is_new_in_batch': player in analysis_result['truly_new_players']
                    }
                }
            }

            updated_database['player_details'].append(player_info)

        # データベース保存
        with open(self.system_files['updated_database'], 'w', encoding='utf-8') as f:
            json.dump(updated_database, f, ensure_ascii=False, indent=2)

        print(f"✅ 更新データベース保存: {self.system_files['updated_database']}")

        return updated_database, updated_confirmed_players, updated_potential_players

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

    def create_updated_response_templates(self, database: Dict, confirmed_players: List[str], potential_players: List[str]):
        """更新応答テンプレート作成"""
        print(f"\n📝 更新応答テンプレート作成")
        print("=" * 35)

        templates = {}
        all_players = confirmed_players + potential_players
        confirmed_count = len(confirmed_players)
        potential_count = len(potential_players)

        # チーム全体テンプレート（更新版）
        templates['team_overview'] = f"{self.team_name}には現在{len(all_players)}名の選手情報があります（確認済み{confirmed_count}名、候補{potential_count}名）。選手一覧: {', '.join(all_players)}。どの選手について詳しく知りたいですか？"

        templates['confirmed_players_list'] = f"確認済み選手一覧（{confirmed_count}名）: {', '.join(confirmed_players)}"

        if potential_players:
            templates['potential_players_list'] = f"候補選手一覧（{potential_count}名）: {', '.join(potential_players)}"

        templates['total_count'] = f"{self.team_name}の現在の選手情報は{len(all_players)}名です。"

        # 各選手用テンプレート
        for player_info in database['player_details']:
            name = player_info['name']
            status = player_info['status']
            order = player_info['registration_order']
            source = player_info['learning_metadata']['source']

            if status == 'confirmed':
                if source == 'promoted_from_potential':
                    templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は{self.team_name}の確認済み選手として新たに正式登録されました。"
                else:
                    templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は{self.team_name}の確認済み選手で、{order}番目に登録されています。"

                templates[f'{name}_detail'] = f"{name}選手は{self.team_name}の正式メンバーです。どのようなことをお知りになりたいですか？"
            else:
                templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は{self.team_name}の候補選手として特定されています。"
                templates[f'{name}_detail'] = f"{name}選手は分析により発見された{self.team_name}のメンバーの可能性があります。詳細情報をお持ちでしたら教えてください。"

            templates[f'{name}_question'] = f"{name}選手について何をお知りになりたいですか？"

        # 更新関連テンプレート
        templates['batch_update_notification'] = f"選手情報を一括更新しました。新たに{len(self.new_provided_players)}名の選手情報をいただき、システムに統合いたしました。"
        templates['new_player_welcome'] = "新しい選手情報をありがとうございます！学習して記憶いたします。"
        templates['status_promotion'] = "候補選手を確認済み選手に昇格させました。"

        # テンプレート保存
        with open(self.system_files['updated_templates'], 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)

        print(f"✅ 更新応答テンプレート保存: {self.system_files['updated_templates']}")
        print(f"📊 作成テンプレート数: {len(templates)}")

        return templates

    def create_batch_learning_log(self, analysis_result: Dict, confirmed_players: List[str]):
        """一括学習ログ作成"""
        print(f"\n📚 一括学習ログ作成")
        print("=" * 25)

        batch_log = {
            'log_info': {
                'created_date': datetime.now().isoformat(),
                'version': '1.1_batch_update',
                'purpose': 'track_batch_player_learning',
                'batch_id': 'batch_001'
            },
            'batch_learning_session': {
                'session_id': 'batch_001_user_provided',
                'date': datetime.now().isoformat(),
                'type': 'user_batch_input',
                'action': 'integrate_new_player_list',
                'input_data': {
                    'provided_players': self.new_provided_players,
                    'player_count': len(self.new_provided_players)
                },
                'processing_results': analysis_result,
                'final_state': {
                    'confirmed_players_count': len(confirmed_players),
                    'confirmed_players': confirmed_players,
                    'total_players': len(confirmed_players)
                }
            },
            'learning_improvements': {
                '翔平_promotion': {
                    'action': 'status_promotion',
                    'from_status': 'potential',
                    'to_status': 'confirmed',
                    'reason': 'user_provided_confirmation'
                },
                'new_players_added': {
                    'count': len(analysis_result['truly_new_players']),
                    'players': analysis_result['truly_new_players'],
                    'source': 'user_direct_input'
                }
            },
            'statistics': {
                'batch_size': len(self.new_provided_players),
                'duplicates_found': len(analysis_result['duplicates']),
                'new_unique_players': len(analysis_result['truly_new_players']),
                'status_promotions': 1 if analysis_result['翔平_status_change'] else 0,
                'learning_accuracy': 'high_confidence_user_input'
            }
        }

        # ログ保存
        with open(self.system_files['batch_learning_log'], 'w', encoding='utf-8') as f:
            json.dump(batch_log, f, ensure_ascii=False, indent=2)

        print(f"✅ 一括学習ログ保存: {self.system_files['batch_learning_log']}")

        return batch_log

    def create_updated_uma3_integration(self, confirmed_players: List[str], potential_players: List[str]):
        """uma3.py統合コード更新版作成"""
        print(f"\n🔗 uma3.py統合コード更新")
        print("=" * 30)

        integration_code = f'''
# 更新版拡張可能選手情報統合（一括学習対応）
class UpdatedExpandablePlayerInfoHandler:
    """更新版拡張可能選手情報ハンドラー"""

    def __init__(self):
        # 確認済み選手（更新版 - {len(confirmed_players)}名）
        self.confirmed_players = {confirmed_players}

        # 候補選手（更新版 - {len(potential_players)}名）
        self.potential_players = {potential_players}

        # 全選手
        self.all_players = self.confirmed_players + self.potential_players
        self.total_players = len(self.all_players)
        self.team_name = "{self.team_name}"

        # 学習・更新機能
        self.expandable = True
        self.can_learn_new_players = True
        self.batch_learning_supported = True

        # 一括更新情報
        self.last_batch_update = "{datetime.now().isoformat()}"
        self.batch_update_count = {len(self.new_provided_players)}

    def find_player_in_message(self, message: str) -> Optional[str]:
        """メッセージから選手名を検出（更新版）"""
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
        """メッセージハンドリング（更新版）"""
        detected_player = self.find_player_in_message(message)

        if detected_player:
            status = self.get_player_status(detected_player)
            player_index = self.all_players.index(detected_player) + 1

            if status == 'confirmed':
                # 翔平の特別処理
                if detected_player == "翔平":
                    return f"{{detected_player}}選手についてお答えします。{{detected_player}}選手は{{self.team_name}}の確認済み選手として新たに正式登録されました。"
                else:
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
            elif '更新' in message or '新しい' in message:
                return f"最新の一括更新で{{self.batch_update_count}}名の選手情報をいただき、システムに統合いたしました。現在{{self.total_players}}名の選手情報があります。"
            else:
                return f"{{self.team_name}}には現在{{self.total_players}}名の選手情報があります。確認済み{{len(self.confirmed_players)}}名、候補{{len(self.potential_players)}}名です。どの選手について詳しく知りたいですか？"

        return None

# グローバル更新版拡張選手情報ハンドラー
updated_expandable_player_handler = UpdatedExpandablePlayerInfoHandler()
'''

        # 統合コード保存
        with open(self.system_files['integration_update'], 'w', encoding='utf-8') as f:
            f.write(integration_code)

        print(f"✅ 更新uma3.py統合コード保存: {self.system_files['integration_update']}")

        return integration_code

def main():
    """メイン処理"""
    print("🚀 新規選手一括学習システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 一括学習システム初期化
    batch_learning = NewPlayerBatchLearning()

    print(f"📊 学習前の状態:")
    print(f"   ✅ 既存確認済み選手: {len(batch_learning.existing_confirmed_players)}名")
    print(f"      {', '.join(batch_learning.existing_confirmed_players)}")
    print(f"   🔍 既存候補選手: {len(batch_learning.existing_potential_players)}名")
    print(f"      {', '.join(batch_learning.existing_potential_players)}")
    print(f"   🆕 新規提供選手: {len(batch_learning.new_provided_players)}名")
    print(f"      {', '.join(batch_learning.new_provided_players)}")
    print()

    # 1. 新規選手分析
    analysis_result = batch_learning.analyze_new_players()

    # 2. 更新データベース作成
    updated_database, confirmed_players, potential_players = batch_learning.create_updated_player_database(analysis_result)

    # 3. 更新応答テンプレート作成
    updated_templates = batch_learning.create_updated_response_templates(updated_database, confirmed_players, potential_players)

    # 4. 一括学習ログ作成
    batch_log = batch_learning.create_batch_learning_log(analysis_result, confirmed_players)

    # 5. 更新uma3.py統合コード作成
    updated_integration = batch_learning.create_updated_uma3_integration(confirmed_players, potential_players)

    print(f"\n🎊 一括学習完了サマリー")
    print("=" * 30)
    print(f"🏆 最終結果:")
    print(f"   ✅ 確認済み選手: {len(confirmed_players)}名")
    print(f"   🔍 候補選手: {len(potential_players)}名")
    print(f"   📈 総選手数: {len(confirmed_players) + len(potential_players)}名")
    print(f"   🆕 今回追加: {len(analysis_result['truly_new_players'])}名")
    print(f"   ⬆️ 昇格選手: {'翔平（候補→確認済み）' if analysis_result['翔平_status_change'] else 'なし'}")

    print(f"\n📁 作成ファイル:")
    for file_key, file_name in batch_learning.system_files.items():
        print(f"   📄 {file_name}")

    print(f"\n🎉 新規選手一括学習システム完了！")
    print(f"✨ {len(batch_learning.new_provided_players)}名の選手情報を正常に統合しました")

if __name__ == "__main__":
    main()
