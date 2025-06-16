from datetime import datetime

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import Http404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account, Bill, Expense, Goal, MainGoal, Transaction, User
from .serializers import (
    AccountSerializer,
    BillSerializer,
    ExpenseSerializer,
    GoalSerializer,
    LoginSerializer,
    MainGoalSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    ProfileSerializer,
    RegisterSerializer,
    TransactionSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"user": RegisterSerializer(user).data, "token": token.key},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "user": {"username": user.username, "email": user.email},
                    "token": token.key,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the user actually has a token
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()
            return Response(
                {"message": "Logout was successful"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"error": "No active token found"}, status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # TODO: Implement email sending
            # send_email(serializer.data['email'], serializer.data['reset_link'])
            return Response(
                {"message": "Password reset link has been sent to your email"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PasswordChangeSerializer)
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProfileSerializer)
    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        user_data = []
        for user in users:
            token = Token.objects.get_or_create(user=user)[0]
            user_data.append({"user": LoginSerializer(user).data, "token": token.key})
        return Response(
            {
                "message": "This is a secure test view",
                "users_with_tokens": user_data,
            }
        )


class TransactionListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = TransactionSerializer(request.user.transactions.all(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TransactionSerializer)
    def post(self, request):
        serializer = TransactionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Transaction.objects.get(pk=pk, user=user)
        except Transaction.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        transaction = self.get_object(pk, request.user)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=TransactionSerializer)
    def put(self, request, pk):
        transaction = self.get_object(pk, request.user)
        serializer = TransactionSerializer(
            transaction, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        transaction = self.get_object(pk, request.user)
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BillListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = BillSerializer(request.user.bills.all(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BillSerializer)
    def post(self, request):
        serializer = BillSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Bill.objects.get(pk=pk, user=user)
        except Bill.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        bill = self.get_object(pk, request.user)
        serializer = BillSerializer(bill)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=BillSerializer)
    def put(self, request, pk):
        bill = self.get_object(pk, request.user)
        serializer = BillSerializer(
            bill, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        bill = self.get_object(pk, request.user)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = AccountSerializer(request.user.accounts.all(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=AccountSerializer)
    def post(self, request):
        serializer = AccountSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Account.objects.get(pk=pk, user=user)
        except Account.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        account = self.get_object(pk, request.user)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=AccountSerializer)
    def put(self, request, pk):
        account = self.get_object(pk, request.user)
        serializer = AccountSerializer(
            account, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        account = self.get_object(pk, request.user)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ExpenseSerializer(request.user.expenses.all(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ExpenseSerializer)
    def post(self, request):
        serializer = ExpenseSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Expense.objects.get(pk=pk, user=user)
        except Expense.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        expense = self.get_object(pk, request.user)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ExpenseSerializer)
    def put(self, request, pk):
        expense = self.get_object(pk, request.user)
        serializer = ExpenseSerializer(
            expense, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(pk, request.user)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoalListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GoalSerializer(request.user.goals.all(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=GoalSerializer)
    def post(self, request):
        serializer = GoalSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoalDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Goal.objects.get(pk=pk, user=user)
        except Goal.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        goal = self.get_object(pk, request.user)
        serializer = GoalSerializer(goal)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=GoalSerializer)
    def put(self, request, pk):
        goal = self.get_object(pk, request.user)
        serializer = GoalSerializer(
            goal, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        goal = self.get_object(pk, request.user)
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseByMonthAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_year = datetime.now().year
        last_year = current_year - 1
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        # Initialize data dictionaries for both years and all months
        monthly_expenses_data = {
            year: {month: 0 for month in months} for year in [last_year, current_year]
        }

        # Fetch and aggregate expenses
        expenses = (
            Expense.objects.filter(
                user=request.user, date__year__in=[last_year, current_year]
            )
            .annotate(month=TruncMonth("date"))
            .values("month", "date__year")
            .annotate(total=Sum("amount"))
            .order_by("date__year", "month")
        )

        # Populate the expenses data
        for expense in expenses:
            year = expense["date__year"]
            month_name = expense["month"].strftime("%B")
            monthly_expenses_data[year][month_name] = expense["total"]

        return Response(monthly_expenses_data)


class ExpenseByCategoryAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_date = timezone.now()
        current_month = current_date.month
        current_year = current_date.year
        last_month = current_month - 1 if current_month > 1 else 12
        last_year = current_year if current_month > 1 else current_year - 1
        CATEGORIES = [
            "housing",
            "food",
            "transportation",
            "entertainment",
            "education",
            "health",
            "shopping",
        ]

        # Initialize category data for detailed current month expenses
        current_month_detailed = {
            category: {"total": 0, "expenses": []} for category in CATEGORIES
        }

        # Fetch detailed current month expenses
        current_month_expenses = Expense.objects.filter(
            user=request.user, date__year=current_year, date__month=current_month
        )

        # Fill category data with actual expenses
        for expense in current_month_expenses:
            serialized_expense = ExpenseSerializer(expense).data
            current_month_detailed[expense.category]["total"] += expense.amount
            current_month_detailed[expense.category]["expenses"].append(
                serialized_expense
            )

        # Aggregate last month expenses by category for comparison
        last_month_expenses = (
            Expense.objects.filter(
                user=request.user, date__year=last_year, date__month=last_month
            )
            .values("category")
            .annotate(total=Sum("amount"))
        )

        # Initialize last month totals for comparison
        last_expenses_dict = {category: 0 for category in CATEGORIES}
        for expense in last_month_expenses:
            last_expenses_dict[expense["category"]] = expense["total"]

        # Calculate percentage change by category
        categorized_expenses = []
        for category in CATEGORIES:
            current_total = current_month_detailed[category]["total"]
            last_total = last_expenses_dict[category]
            percentage_change = (
                ((current_total - last_total) / last_total) * 100
                if last_total > 0
                else (100 if current_total > 0 else 0)
            )

            categorized_expenses.append(
                {
                    "category": category,
                    "current_month_total": current_total,
                    "last_month_total": last_total,
                    "percentage_change": round(percentage_change, 2),
                }
            )

        # Construct the response
        response = {
            "categorized_expenses": categorized_expenses,
            "current_month_expenses": current_month_detailed,
        }

        return Response(response)


class MainGoalAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MainGoalSerializer(request.user.main_goal.all(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=MainGoalSerializer)
    def post(self, request):
        existing_goal = MainGoal.first()
        if existing_goal:
            # If a goal exists, update it instead of creating a new one
            serializer = MainGoalSerializer(
                existing_goal, data=request.data, context={"request": request}
            )
            action = "updated"
        else:
            # No existing goal, create a new one
            serializer = MainGoalSerializer(
                data=request.data, context={"request": request}
            )
            action = "created"

        if serializer.is_valid():
            serializer.save(user=request.user)  # Ensure the user is set
            return Response(
                {
                    "message": f"Main goal successfully {action}.",
                    "data": serializer.data,
                },
                status=(
                    status.HTTP_201_CREATED
                    if action == "created"
                    else status.HTTP_200_OK
                ),
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoalByMonthAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_year = timezone.now().year
        last_year = current_year - 1
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        # Initialize data dictionaries for both years and all months
        monthly_goals_data = {
            year: {month: 0 for month in months} for year in [last_year, current_year]
        }

        # Fetch and aggregate goals
        goals = (
            Goal.objects.filter(
                user=request.user, start_date__year__in=[last_year, current_year]
            )
            .annotate(month=TruncMonth("start_date"))
            .values("month", "start_date__year")
            .annotate(total_achieved=Sum("achieved_amount"))
            .order_by("start_date__year", "month")
        )

        # Populate the goals data
        for goal in goals:
            year = goal["start_date__year"]
            month_name = goal["month"].strftime("%B")
            monthly_goals_data[year][month_name] = goal["total_achieved"]

        return Response(monthly_goals_data)


class GoalByCategoryAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_date = timezone.now()
        current_month = current_date.month
        current_year = current_date.year
        CATEGORIES = [
            "housing",
            "food",
            "transportation",
            "entertainment",
            "education",
            "health",
            "shopping",
        ]

        # Initialize category data
        category_data = {
            category: {"totalAchievedAmount": 0, "totalTargetAmount": 0}
            for category in CATEGORIES
        }

        # Fetch goals for the current month
        current_month_goals = Goal.objects.filter(
            user=request.user,
            start_date__year=current_year,
            start_date__month=current_month,
        )

        # Fill category data with actual goals
        for goal in current_month_goals:
            category_data[goal.category]["totalAchievedAmount"] += goal.achieved_amount
            category_data[goal.category]["totalTargetAmount"] += goal.target_amount

        # Calculate the percentage of completion for each category
        categorized_goals = []
        for category in CATEGORIES:
            total_achieved = category_data[category]["totalAchievedAmount"]
            total_target = category_data[category]["totalTargetAmount"]
            percentage = (
                (total_achieved / total_target * 100) if total_target > 0 else 0
            )

            categorized_goals.append(
                {
                    "category": category,
                    "total_achieved_amount": total_achieved,
                    "total_target_amount": total_target,
                    "percentage": round(percentage, 2),
                }
            )

        # Construct the response
        response = {"current_month_categorized_goals": categorized_goals}

        return Response(response)


class DashboardAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch user
        user = request.user
        # Required vars
        current_date = timezone.now()
        current_month = current_date.month
        current_year = current_date.year
        last_month = current_month - 1 if current_month > 1 else 12
        last_year = current_year if current_month > 1 else current_year - 1
        previous_year = current_year - 1
        CATEGORIES = [
            "housing",
            "food",
            "transportation",
            "entertainment",
            "education",
            "health",
            "shopping",
        ]
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        # Total balance and accounts data
        total_balance = Account.objects.filter(user=user).aggregate(Sum("balance"))
        accounts = Account.objects.filter(user=user)
        accounts_serializer = AccountSerializer(accounts, many=True)

        # Recent transactions data
        recent_transactions = Transaction.objects.filter(user=user).order_by("-date")[
            :5
        ]
        transactions_serializer = TransactionSerializer(recent_transactions, many=True)

        # Main goal data
        main_goal = MainGoal.objects.filter(user=user).first()
        main_goal_serializer = MainGoalSerializer(main_goal)

        # Expenses data for chart
        # Initialize data dictionaries for both years and all months
        monthly_expenses_data = {
            year: {month: 0 for month in months}
            for year in [previous_year, current_year]
        }
        # Fetch and aggregate expenses
        expenses = (
            Expense.objects.filter(
                user=user, date__year__in=[previous_year, current_year]
            )
            .annotate(month=TruncMonth("date"))
            .values("month", "date__year")
            .annotate(total=Sum("amount"))
            .order_by("date__year", "month")
        )

        # Populate the expenses data
        for expense in expenses:
            year = expense["date__year"]
            month_name = expense["month"].strftime("%B")
            monthly_expenses_data[year][month_name] = expense["total"]

        # Goals data for chart
        # Initialize data dictionaries for both years and all months
        monthly_goals_data = {
            year: {month: 0 for month in months}
            for year in [previous_year, current_year]
        }
        # Fetch and aggregate goals
        goals = (
            Goal.objects.filter(
                user=user, start_date__year__in=[previous_year, current_year]
            )
            .annotate(month=TruncMonth("start_date"))
            .values("month", "start_date__year")
            .annotate(total_achieved=Sum("achieved_amount"))
            .order_by("start_date__year", "month")
        )

        # Populate the goals data
        for goal in goals:
            year = goal["start_date__year"]
            month_name = goal["month"].strftime("%B")
            monthly_goals_data[year][month_name] = goal["total_achieved"]

        # Categorized expenses data
        # Fetch current month expenses by category
        current_month_expenses = (
            Expense.objects.filter(
                user=request.user, date__year=current_year, date__month=current_month
            )
            .values("category")
            .annotate(total=Sum("amount"))
        )

        # Convert QuerySet to dictionary
        current_expenses_dict = {
            item["category"]: item["total"] for item in current_month_expenses
        }

        # Fetch last month expenses by category
        last_month_expenses = (
            Expense.objects.filter(
                user=request.user, date__year=last_year, date__month=last_month
            )
            .values("category")
            .annotate(total=Sum("amount"))
        )

        # Convert QuerySet to dictionary
        last_expenses_dict = {
            item["category"]: item["total"] for item in last_month_expenses
        }

        # Calculate percentage change by category
        categorized_expenses = []
        for category in CATEGORIES:
            current_total = current_expenses_dict.get(category, 0)
            last_total = last_expenses_dict.get(category, 0)
            percentage_change = (
                ((current_total - last_total) / last_total) * 100
                if last_total > 0
                else (100 if current_total > 0 else 0)
            )
            categorized_expenses.append(
                {
                    "category": category,
                    "current_month_total": current_total,
                    "last_month_total": last_total,
                    "percentage_change": round(percentage_change, 2),
                }
            )

        # Response
        response_data = {
            "user": user.username,
            "date": current_date.strftime("%d-%m-%Y"),
            "total_balance": total_balance["balance__sum"],
            "accounts": accounts_serializer.data,
            "main_goal": main_goal_serializer.data,
            "recent_transactions": transactions_serializer.data,
            "monthly_goals": monthly_goals_data,
            "monthly_expenses": monthly_expenses_data,
            "categorized_expenses": categorized_expenses,
        }

        return Response(response_data)
