# core/management/commands/create_tenant.py

from django.core.management.base import BaseCommand
from core.utils import create_tenant


class Command(BaseCommand):
    help = "Creates a new tenant and their associated database"

    def add_arguments(self, parser):
        parser.add_argument('student_id', type=str)

    def handle(self, *args, **kwargs):
        # Get the values of the arguments
        student_id = kwargs['student_id']

        # Call the function to create the tenant
        tenant = create_tenant(student_id)

        if tenant:
            self.stdout.write(self.style.SUCCESS(f"Tenant '{student_id}' created successfully:\n{tenant}\n"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to create tenant '{student_id}'."))
