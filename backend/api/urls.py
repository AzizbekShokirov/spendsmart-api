from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    TestView,
    PasswordChangeView,
    PasswordResetView,
    TransactionListCreateAPIView,
    TransactionDetailAPIView,
    BillListCreateAPIView,
    BillDetailAPIView,
    AccountListCreateAPIView,
    AccountDetailAPIView,
    ExpenseListCreateAPIView,
    ExpenseDetailAPIView,
    ExpenseByMonthAPIView,
    ExpenseByCategoryAPIView,
    GoalListCreateAPIView,
    GoalDetailAPIView,
    MainGoalAPIView,
    GoalByMonthAPIView,
    GoalByCategoryAPIView,
    DashboardAPIView,
    ProfileView,
)

urlpatterns = [
    # Auth URLs
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("test-view/", TestView.as_view(), name="test-view"),
    # Password Reset URLs
    path("password_change/", PasswordChangeView.as_view(), name="password-change"),
    path("password_reset/", PasswordResetView.as_view(), name="password-reset"),
    # Transaction URLs
    path(
        "transactions/", TransactionListCreateAPIView.as_view(), name="transaction-list"
    ),
    path(
        "transactions/<int:pk>/",
        TransactionDetailAPIView.as_view(),
        name="transaction-detail",
    ),
    # Bill URLs
    path("bills/", BillListCreateAPIView.as_view(), name="bill-list"),
    path("bills/<int:pk>/", BillDetailAPIView.as_view(), name="bill-detail"),
    # Account URLs
    path("accounts/", AccountListCreateAPIView.as_view(), name="account-list"),
    path("accounts/<int:pk>/", AccountDetailAPIView.as_view(), name="account-detail"),
    # Expense URLs
    path("expenses/", ExpenseListCreateAPIView.as_view(), name="expense-list"),
    path("expenses/<int:pk>/", ExpenseDetailAPIView.as_view(), name="expense-detail"),
    path("expenses/monthly/", ExpenseByMonthAPIView.as_view(), name="monthly-expenses"),
    path(
        "expenses/category/",
        ExpenseByCategoryAPIView.as_view(),
        name="category-expense",
    ),
    # Goal URLs
    path("goals/", GoalListCreateAPIView.as_view(), name="goal-list"),
    path("goals/<int:pk>/", GoalDetailAPIView.as_view(), name="goal-detail"),
    path("goals/main/", MainGoalAPIView.as_view(), name="main-goal"),
    path("goals/monthly/", GoalByMonthAPIView.as_view(), name="monthly-goals"),
    path("goals/category/", GoalByCategoryAPIView.as_view(), name="category-goals"),
    # URL
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
