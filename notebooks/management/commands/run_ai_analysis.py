# notebooks/management/commands/run_ai_analysis.py
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from notebooks.models import Notebook, Entry
from notebooks.views import batch_ai_analysis_for_user, perform_ai_analysis_for_notebook, perform_ai_analysis_for_entry


class Command(BaseCommand):
    help = 'ノートブックとエントリーに対してAI分析を実行します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='特定のユーザーのみ処理（ユーザー名を指定）',
        )
        parser.add_argument(
            '--notebook',
            type=str,
            help='特定のノートブックのみ処理（ノートブックIDを指定）',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='既にAI分析済みのデータも強制的に再分析',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='実際の処理は行わず、対象データの確認のみ',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='処理するノートブック数の上限（デフォルト: 100）',
        )

    def handle(self, *args, **options):
        force_update = options['force']
        dry_run = options['dry_run']
        limit = options['limit']
        
        self.stdout.write(self.style.SUCCESS('AI分析バッチ処理を開始します'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN モード: 実際の処理は行いません'))

        # 特定のノートブック処理
        if options['notebook']:
            self.process_specific_notebook(options['notebook'], force_update, dry_run)
            return

        # 特定のユーザー処理
        if options['user']:
            self.process_specific_user(options['user'], force_update, dry_run, limit)
            return

        # 全ユーザー処理
        self.process_all_users(force_update, dry_run, limit)

    def process_specific_notebook(self, notebook_id, force_update, dry_run):
        """特定のノートブック処理"""
        try:
            notebook = Notebook.objects.get(pk=notebook_id)
            
            self.stdout.write(f'ノートブック処理: {notebook.title} (ID: {notebook_id})')
            
            if dry_run:
                self.stdout.write(f'  - エントリー数: {notebook.entries.count()}')
                if notebook.ai_last_analyzed and not force_update:
                    self.stdout.write(f'  - 既に分析済み: {notebook.ai_last_analyzed}')
                else:
                    self.stdout.write('  - 分析対象')
                return

            # ノートブック分析
            if force_update or not notebook.ai_last_analyzed:
                perform_ai_analysis_for_notebook(notebook)
                self.stdout.write(self.style.SUCCESS(f'  ✓ ノートブック分析完了'))

            # エントリー分析
            entries_processed = 0
            for entry in notebook.entries.all():
                if force_update or not entry.ai_analysis_cache:
                    perform_ai_analysis_for_entry(entry)
                    entries_processed += 1

            self.stdout.write(self.style.SUCCESS(f'  ✓ エントリー分析完了: {entries_processed}件'))

        except Notebook.DoesNotExist:
            raise CommandError(f'ノートブック ID "{notebook_id}" が見つかりません')

    def process_specific_user(self, username, force_update, dry_run, limit):
        """特定のユーザー処理"""
        try:
            user = User.objects.get(username=username)
            
            notebooks = Notebook.objects.filter(user=user)[:limit]
            
            self.stdout.write(f'ユーザー処理: {username} (ノートブック数: {notebooks.count()})')
            
            if dry_run:
                self.show_analysis_summary(notebooks, force_update)
                return

            success_count = 0
            for notebook in notebooks:
                try:
                    if force_update or not notebook.ai_last_analyzed:
                        perform_ai_analysis_for_notebook(notebook)
                        
                    # エントリー分析
                    for entry in notebook.entries.all():
                        if force_update or not entry.ai_analysis_cache:
                            perform_ai_analysis_for_entry(entry)
                    
                    success_count += 1
                    self.stdout.write(f'  ✓ {notebook.title}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ {notebook.title}: {str(e)}')
                    )

            self.stdout.write(
                self.style.SUCCESS(f'完了: {success_count}/{notebooks.count()} ノートブック処理')
            )

        except User.DoesNotExist:
            raise CommandError(f'ユーザー "{username}" が見つかりません')

    def process_all_users(self, force_update, dry_run, limit):
        """全ユーザー処理"""
        users = User.objects.filter(notebook__isnull=False).distinct()
        
        self.stdout.write(f'全ユーザー処理: {users.count()}ユーザー')
        
        if dry_run:
            total_notebooks = 0
            total_entries = 0
            
            for user in users:
                notebooks = Notebook.objects.filter(user=user)[:limit]
                entries = Entry.objects.filter(notebook__user=user)
                
                total_notebooks += notebooks.count()
                total_entries += entries.count()
                
                analyzed_notebooks = notebooks.filter(ai_last_analyzed__isnull=False).count()
                analyzed_entries = entries.exclude(ai_analysis_cache={}).count()
                
                self.stdout.write(
                    f'  {user.username}: ノート{notebooks.count()}件 '
                    f'(分析済み{analyzed_notebooks}件), '
                    f'エントリー{entries.count()}件 (分析済み{analyzed_entries}件)'
                )
            
            self.stdout.write(f'合計: ノート{total_notebooks}件, エントリー{total_entries}件')
            return

        total_processed = 0
        total_success = 0
        
        for user in users:
            self.stdout.write(f'処理中: {user.username}')
            
            try:
                if batch_ai_analysis_for_user(user.id, force_update):
                    total_success += 1
                total_processed += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ ユーザー {user.username}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'全体完了: {total_success}/{total_processed} ユーザー処理')
        )

    def show_analysis_summary(self, notebooks, force_update):
        """分析サマリー表示（DRY RUN用）"""
        total_notebooks = notebooks.count()
        analyzed_notebooks = notebooks.filter(ai_last_analyzed__isnull=False).count()
        
        if force_update:
            target_notebooks = total_notebooks
        else:
            target_notebooks = total_notebooks - analyzed_notebooks

        total_entries = Entry.objects.filter(notebook__in=notebooks).count()
        analyzed_entries = Entry.objects.filter(
            notebook__in=notebooks
        ).exclude(ai_analysis_cache={}).count()
        
        if force_update:
            target_entries = total_entries
        else:
            target_entries = total_entries - analyzed_entries

        self.stdout.write('分析対象サマリー:')
        self.stdout.write(f'  ノートブック: {target_notebooks}/{total_notebooks}件')
        self.stdout.write(f'  エントリー: {target_entries}/{total_entries}件')

        if not force_update:
            self.stdout.write(
                self.style.WARNING('既に分析済みのデータはスキップされます（--force で強制実行）')
            )