from django.contrib import admin
from .models import Transaction, Account, Bill, Expense, Goal, MainGoal, User


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "date", "user")
    list_filter = ("date", "user")
    search_fields = ("title", "user__username")


class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_type", "account_number", "balance", "user")
    list_filter = ("account_type", "user")
    search_fields = ("account_number",)


class BillAdmin(admin.ModelAdmin):
    list_display = ("title", "due_date", "amount", "user")
    list_filter = ("due_date",)
    search_fields = ("title",)


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "amount", "date", "user")
    list_filter = ("date", "category")
    search_fields = ("title",)


class CategoryGoalAdmin(admin.ModelAdmin):
    list_display = ("category", "target_amount", "user")
    list_filter = ("category", "user")
    search_fields = ("category",)


class MainGoalAdmin(admin.ModelAdmin):
    list_display = (
        "target_amount",
        "achieved_amount",
        "start_date",
        "end_date",
        "user",
    )
    list_filter = ("start_date", "end_date")
    search_fields = ("title",)


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "phone_number")
    search_fields = ("username", "email")


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Goal, CategoryGoalAdmin)
admin.site.register(MainGoal, MainGoalAdmin)
admin.site.register(User, UserAdmin)
