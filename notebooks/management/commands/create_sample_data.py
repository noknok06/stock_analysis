# notebooks/management/commands/create_sample_data.py（最終版）
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notebooks.models import Notebook, Entry

class Command(BaseCommand):
    help = 'サンプルデータを作成します（最終版）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='admin',
            help='サンプルデータを作成するユーザー名（デフォルト: admin）',
        )

    def handle(self, *args, **options):
        try:
            username = options['user']
            
            # ユーザーを取得または作成
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com', 
                    'is_staff': True, 
                    'is_superuser': True
                }
            )
            if created:
                user.set_password('admin123')
                user.save()
                self.stdout.write(f'ユーザー {user.username} を作成しました')
            else:
                self.stdout.write(f'既存ユーザー {user.username} を使用します')

            # 既存のサンプルデータを削除
            existing_count = Notebook.objects.filter(user=user, stock_code__in=['7203', '6758', '9984']).count()
            if existing_count > 0:
                Notebook.objects.filter(user=user, stock_code__in=['7203', '6758', '9984']).delete()
                self.stdout.write(f'既存のサンプルデータ {existing_count}件を削除しました')

            # サンプルノートブックを作成
            sample_notebooks = [
                {
                    'stock_code': '7203',
                    'company_name': 'トヨタ自動車',
                    'subtitle': '長期保有・配当重視',
                    'investment_goal': '安定配当を重視した長期投資。自動車業界のリーダーとして持続的成長を期待。',
                    'current_price': 2845.0,
                    'target_price': 3200.0,
                    'risk_factors': 'EV移行リスク、為替変動、半導体不足',
                    'tags': ['高配当', '自動車', '長期投資', '決算分析']
                },
                {
                    'stock_code': '6758',
                    'company_name': 'ソニー',
                    'subtitle': 'エンタメ事業分析',
                    'investment_goal': 'ゲーム・音楽・映画事業の成長性に注目。デジタル化の恩恵を受ける企業として評価。',
                    'current_price': 12000.0,
                    'target_price': 15000.0,
                    'risk_factors': '競合激化、為替影響、技術革新リスク',
                    'tags': ['成長株', 'IT', 'エンタメ', 'ゲーム']
                },
                {
                    'stock_code': '9984',
                    'company_name': 'ソフトバンク',
                    'subtitle': '通信株として評価',
                    'investment_goal': '5G展開とAI投資による中長期成長。通信インフラの安定性を評価。',
                    'current_price': 1542.0,
                    'target_price': 1800.0,
                    'risk_factors': '通信規制、投資負担、競合激化',
                    'tags': ['通信', '5G', 'AI', 'インフラ']
                }
            ]

            for notebook_data in sample_notebooks:
                try:
                    tags = notebook_data.pop('tags')
                    notebook_data['user'] = user
                    notebook_data['title'] = f"{notebook_data['stock_code']} {notebook_data['company_name']}"
                    
                    self.stdout.write(f'ノートブック作成中: {notebook_data["title"]}')
                    
                    # 新しいノートブック作成
                    notebook = Notebook.objects.create(**notebook_data)
                    self.stdout.write(f'ノートブック作成成功: ID={notebook.pk}')
                    
                    # タグを追加
                    try:
                        notebook.tags.add(*tags)
                        self.stdout.write(f'タグ追加成功: {", ".join(tags)}')
                    except Exception as e:
                        self.stdout.write(f'タグ追加エラー: {str(e)}')
                    
                    # サンプルエントリーを作成
                    sample_entries = [
                        {
                            'entry_type': 'analysis',
                            'title': 'Q3決算分析',
                            'content': '売上高は前年同期比12%増。営業利益も順調に成長している。特に海外展開が好調。',
                            'tags': ['決算分析', '業績好調']
                        },
                        {
                            'entry_type': 'memo',
                            'title': '投資メモ',
                            'content': '長期的な視点で保有継続。配当も安定している。',
                            'tags': ['投資判断', '長期保有']
                        }
                    ]
                    
                    for entry_data in sample_entries:
                        try:
                            entry_tags = entry_data.pop('tags')
                            entry_data['notebook'] = notebook
                            
                            entry = Entry.objects.create(**entry_data)
                            entry.tags.add(*entry_tags)
                            self.stdout.write(f'エントリー作成成功: {entry.title}')
                        except Exception as e:
                            self.stdout.write(f'エントリー作成エラー: {str(e)}')
                    
                    # エントリー数を更新
                    notebook.entry_count = notebook.entries.count()
                    notebook.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ ノートブック "{notebook.title}" 作成完了（エントリー数: {notebook.entry_count}）')
                    )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ ノートブック作成エラー: {str(e)}')
                    )
                    import traceback
                    self.stdout.write(f'詳細エラー: {traceback.format_exc()}')

            # 作成されたノートブック数を確認
            created_count = Notebook.objects.filter(user=user).count()
            self.stdout.write(
                self.style.SUCCESS(f'🎉 サンプルデータの作成が完了しました！（合計: {created_count}件のノートブック）')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'サンプルデータ作成中にエラーが発生しました: {str(e)}')
            )
            import traceback
            self.stdout.write(f'詳細エラー: {traceback.format_exc()}')