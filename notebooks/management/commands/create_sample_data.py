# notebooks/management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notebooks.models import Notebook, Entry
from decimal import Decimal

class Command(BaseCommand):
    help = 'サンプルデータを作成します'

    def handle(self, *args, **options):
        print("Command モジュールが読み込まれました")
        # スーパーユーザーを取得または作成
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('admin')
            user.save()
            self.stdout.write(f'ユーザー {user.username} を作成しました')

        # サンプルノートブックを作成
        sample_notebooks = [
            {
                'stock_code': '7203',
                'company_name': 'トヨタ自動車',
                'subtitle': '長期保有・配当重視',
                'investment_goal': '安定配当を重視した長期投資。自動車業界のリーダーとして持続的成長を期待。',
                'current_price': Decimal('2845.00'),
                'target_price': Decimal('3200.00'),
                'risk_factors': 'EV移行リスク、為替変動、半導体不足',
                'tags': ['高配当', '自動車', '長期投資', '決算分析']
            },
            {
                'stock_code': '6758',
                'company_name': 'ソニー',
                'subtitle': 'エンタメ事業分析',
                'investment_goal': 'ゲーム・音楽・映画事業の成長性に注目。デジタル化の恩恵を受ける企業として評価。',
                'current_price': Decimal('13280.00'),
                'target_price': Decimal('15000.00'),
                'risk_factors': '競合激化、為替影響、技術革新リスク',
                'tags': ['成長株', 'IT', 'エンタメ', 'ゲーム']
            },
            {
                'stock_code': '9984',
                'company_name': 'ソフトバンク',
                'subtitle': '通信株として評価',
                'investment_goal': '5G展開とAI投資による中長期成長。通信インフラの安定性を評価。',
                'current_price': Decimal('1542.00'),
                'target_price': Decimal('1800.00'),
                'risk_factors': '通信規制、投資負担、競合激化',
                'tags': ['通信', '5G', 'AI', 'インフラ']
            }
        ]

        for notebook_data in sample_notebooks:
            tags = notebook_data.pop('tags')
            notebook_data['user'] = user
            notebook_data['title'] = f"{notebook_data['stock_code']} {notebook_data['company_name']}"
            
            notebook, created = Notebook.objects.get_or_create(
                stock_code=notebook_data['stock_code'],
                user=user,
                defaults=notebook_data
            )
            
            if created:
                notebook.tags.add(*tags)
                self.stdout.write(f'ノートブック {notebook.title} を作成しました')
                
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
                    entry_tags = entry_data.pop('tags')
                    entry_data['notebook'] = notebook
                    
                    entry = Entry.objects.create(**entry_data)
                    entry.tags.add(*entry_tags)
                    
                # エントリー数を更新
                notebook.entry_count = notebook.entries.count()
                notebook.save()

        self.stdout.write(
            self.style.SUCCESS('サンプルデータの作成が完了しました')
        )