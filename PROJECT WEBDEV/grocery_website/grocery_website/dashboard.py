"""
This file was generated with the customdashboard management command, it contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.
"""

from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomDashboard(Dashboard):
    """
    Custom dashboard for grocery store
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # Store Management
        self.children.append(modules.ModelList(
            _('Store Management'),
            column=1,
            collapsible=False,
            models=(
                'store.models.Product',
                'store.models.Category',
                'store.models.attacarousel',
            ),
        ))

        # Order Management
        self.children.append(modules.ModelList(
            _('Order Management'),
            column=1,
            collapsible=False,
            models=(
                'store.models.Order',
                'store.models.OrderItem',
                'store.models.Cart',
                'store.models.CartItem',
            ),
        ))

        # User Management
        self.children.append(modules.ModelList(
            _('User Management'),
            column=2,
            collapsible=False,
            models=(
                'store.models.RegisterUser',
                'store.models.Address',
            ),
        ))

        # Customer Feedback
        self.children.append(modules.ModelList(
            _('Customer Feedback'),
            column=2,
            collapsible=False,
            models=(
                'store.models.ProductReview',
            ),
        ))

        # Recent Actions
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            collapsible=False,
            column=3,
        ))

        # Quick Links
        self.children.append(modules.LinkList(
            _('Quick Links'),
            column=3,
            children=[
                {
                    'title': _('Return to site'),
                    'url': '/',
                    'external': False,
                },
                {
                    'title': _('Change password'),
                    'url': 'admin:password_change',
                    'external': False,
                },
                {
                    'title': _('Log out'),
                    'url': 'admin:logout',
                    'external': False,
                },
            ]
        ))

        # Statistics Module
        self.children.append(modules.DashboardModule(
            _('Store Statistics'),
            column=3,
            collapsible=True,
            pre_content="""
            <div style="padding: 10px;">
                <p>Welcome to your store dashboard!</p>
                <p>Here you can manage your entire store operations.</p>
            </div>
            """
        )) 