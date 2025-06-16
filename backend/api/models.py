from django.db import models
from django.contrib.auth.models import AbstractUser


account_choices = (
    ("credit", "Credit"),
    ("checking", "Checking"),
    ("savings", "Savings"),
    ("investment", "Investment"),
    ("loan", "Loan"),
)

category_choices = (
    ("housing", "Housing"),
    ("food", "Food"),
    ("transportation", "Transportation"),
    ("entertainment", "Entertainment"),
    ("education", "Education"),
    ("health", "Health"),
    ("shopping", "Shopping"),
)


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    photo = models.ImageField(
        upload_to="img/profile", default="img/profile/default.jpg"
    )

    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name_plural = "Users"


class Transaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    title = models.CharField(max_length=100)
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"User: {self.user} | Amout: {self.amount} | Date: {self.date}"

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Transactions"


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    account_type = models.CharField(max_length=50, choices=account_choices)
    account_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    organization_name = models.CharField(max_length=100)

    def __str__(self):
        return f"User: {self.user.username} | Account number: {self.account_number}"

    class Meta:
        verbose_name_plural = "Accounts"
        ordering = ["account_type"]


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bills")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recurring = models.BooleanField(default=True)

    def __str__(self):
        return f"User: {self.user} | Title: {self.title} | Amout: {self.amount} | Due date: {self.due_date}"

    class Meta:
        verbose_name_plural = "Bills"
        ordering = ["-due_date"]


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    category = models.CharField(max_length=50, choices=category_choices)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"User: {self.user} | Title: {self.title} | Amount: {self.amount} | Date: {self.date}"

    class Meta:
        verbose_name_plural = "Expenses"
        ordering = ["-date"]


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    category = models.CharField(max_length=50, choices=category_choices)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"User: {self.user} | Category: {self.category} | Target: {self.target_amount} | Achieved: {self.achieved_amount}"

    class Meta:
        verbose_name_plural = "Goals"
        ordering = ["start_date"]


class MainGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="main_goal")
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"User: {self.user} | Target: {self.target_amount} | Achieved: {self.achieved_amount}"

    class Meta:
        verbose_name_plural = "Main Goals"
        ordering = ["start_date"]
