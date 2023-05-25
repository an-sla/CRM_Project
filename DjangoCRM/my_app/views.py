from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomerData
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from .models import CustomerPersonalData
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
from .models import SupportRequest
from .forms import SupportForm
from mailjet_rest import Client
from mailjet_email import send_email
import json
import os
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from catboost import CatBoostClassifier
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            pass
    else:
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)


def home(request):
    if request.user.is_authenticated:
        user = request.user
        all_customers = CustomerData.objects.all()
        context = {'logout_button': True, 'show_welcome_message': True}

        all_customers_df = pd.DataFrame.from_records(all_customers.values())
        colours = ['#00C8F0', '#D2FADF']

        figs = []
        if not user.is_superuser:
            user_customers = CustomerData.objects.filter(user=user)
            user_customers_df = pd.DataFrame.from_records(user_customers.values())

            all_customers_df['Cohort'] = False
            matching_indices = all_customers_df.index.isin(user_customers_df.index)
            all_customers_df.loc[matching_indices, 'Cohort'] = True

            all_customers_df['user_custs'] = 1
            all_customers_df.loc[matching_indices, 'user_custs'] = 150

            # Histograms:
            hist_columns = ['satisfaction_score', 'cltv', 'number_of_referrals', 'tenure_in_months',
                            'avg_monthly_long_distance_charges', 'avg_monthly_gb_download', 'monthly_charge',
                            'total_long_distance_charges', 'total_charges', 'total_extra_data_charges',
                            'total_refunds', 'age']
            hist_labels = ['Score', 'Lifetime value', 'Number of referrals', 'Tenure in months',
                           'Average long-distance charges per month', 'Average GB downloaded per month',
                           'Monthly charges', 'Total long-distance charges', 'Total charges',
                           'Total extra data charges', 'Total refunds', 'Age'
                           ]
            xbins_size = [None, 500, 1, 10, 5, 5, 5, 100, 500, 10, 10, 2]
            for column, label, bins in zip(hist_columns, hist_labels, xbins_size):
                fig = go.Figure()
                fig.add_trace(go.Histogram(histnorm="percent", x=all_customers_df[column], name="All customers",
                                           hovertemplate='<b>% of customers</b>: %{y:.0f} %' +
                                           '<br><b>' + label + ' </b>: %{x}<br><extra></extra>',
                                           marker=dict(color=colours[1]),
                                           xbins=go.histogram.XBins(size=bins)
                                           ))
                fig.add_trace(go.Histogram(histnorm="percent", x=user_customers_df[column],
                                           name="User cohort", hovertemplate='<b>% of customers</b>: %{y:.0f} %' +
                                                                             '<br><b><extra></extra>' + label +
                                                                             ' </b>: %{x}<br>',
                                           marker=dict(color=colours[0]),
                                           xbins=go.histogram.XBins(size=bins)
                                           ))
                figs.append(fig)

            # Piecharts:
            pie_columns = ['phone_service', 'multiple_lines', 'premium_tech_support',
                           'streaming_tv', 'streaming_movies', 'streaming_music', 'internet_type', 'online_security',
                           'online_backup', 'unlimited_data', 'offer', 'contract', 'paperless_billing',
                           'payment_method', 'gender', 'married', 'number_of_dependents']
            for column in pie_columns:
                if column != 'married':
                    all_customers_df[column] = all_customers_df[column].replace(
                        {False: 'Not subscribed', True: 'Subscribed'})
                    user_customers_df[column] = user_customers_df[column].replace({False: 'Not subscribed',
                                                                                   True: 'Subscribed'})
                elif column == 'married':
                    all_customers_df[column] = all_customers_df[column].replace(
                        {False: 'Not married', True: 'Married'})
                    user_customers_df[column] = user_customers_df[column].replace({False: 'Not married',
                                                                                   True: 'Married'})
            for column in pie_columns:
                user_colours = ['#91E2F2', '#00C8F0', '#009DBD', '#108BA3', '#0B5F70', '#08434F']
                all_cust_colours = ['#D2FADF', '#9FBDA9', '79A387', '#5E7064', '#4D5C52', '#455249', '#3C473F']
                fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])
                fig.add_trace(go.Pie(
                    title='All customers',
                    labels=all_customers_df[column].value_counts().index,
                    values=all_customers_df[column].value_counts().values,
                    marker=dict(colors=all_cust_colours),
                    hovertemplate='<b>Number of customers</b>: %{value} <extra></extra>',
                    legendgroup=1
                ),
                    row=1, col=1)

                fig.add_trace(go.Pie(
                    title='User cohort',
                    labels=user_customers_df[column].value_counts().index,
                    values=user_customers_df[column].value_counts().values,
                    marker=dict(colors=user_colours),
                    hovertemplate='<b>Number of customers</b>: %{value} <extra></extra>',
                    legendgroup=2
                ),
                    row=1, col=2)

                figs.append(fig)

            # Geographical map:
            all_customers_df['Cohort'] = all_customers_df['Cohort'].replace(
                {False: 'All customers', True: 'User cohort'})
            fig_geo = px.scatter_mapbox(all_customers_df, lat="latitude", lon="longitude", custom_data=["population"],
                                        color='Cohort', size='user_custs',
                                        zoom=4.15,
                                        center={'lat': 37.4, 'lon': -119}, opacity=0.7,
                                        color_discrete_sequence=colours)
            fig_geo.update_layout(mapbox_accesstoken=
                                  'pk.eyJ1IjoiYW5zbGEiLCJhIjoiY2xkbmU5cG5iMGlobjNudDZhZzc1NzJubiJ9.CAU3T2DiIemshmPHuO6LSA',
                                  margin=dict(l=0, r=0, t=0, b=0))
            fig_geo.update_layout(paper_bgcolor='black')
            fig_geo.update_traces(hovertemplate='<b>Population</b>: %{customdata[0]}<extra></extra>')
            fig_geo.update_layout(title='Geographical distribution')

        else:
            # Histograms:
            columns = ['satisfaction_score', 'cltv', 'number_of_referrals', 'tenure_in_months',
                       'avg_monthly_long_distance_charges', 'avg_monthly_gb_download', 'monthly_charge',
                       'total_long_distance_charges', 'total_charges', 'total_extra_data_charges',
                       'total_refunds', 'age']
            labels = ['Score', 'Lifetime value', 'Number of referrals', 'Tenure in months',
                      'Average long-distance charges per month', 'Average GB downloaded per month',
                      'Monthly charges', 'Total long-distance charges', 'Total charges',
                      'Total extra data charges', 'Total refunds', 'Age'
                      ]
            xbins_size = [None, 500, 1, 10, 5, 5, 5, 100, 500, 10, 10, 1]
            for column, label, bins in zip(columns, labels, xbins_size):
                fig = go.Figure()
                fig.add_trace(go.Histogram(histnorm="percent", x=all_customers_df[column], name="All customers",
                                           hovertemplate='<b>% of customers</b>: %{y:.0f} %' +
                                           '<br><b>' + label + ' </b>: %{x}<br><extra></extra>',
                                           marker=dict(color=colours[1]),
                                           xbins=go.histogram.XBins(size=bins)
                                           ))
                figs.append(fig)

            # Piecharts:
            pie_columns = ['phone_service', 'multiple_lines', 'premium_tech_support',
                           'streaming_tv', 'streaming_movies', 'streaming_music', 'internet_type', 'online_security',
                           'online_backup', 'unlimited_data', 'offer', 'contract', 'paperless_billing',
                           'payment_method', 'gender', 'married', 'number_of_dependents']
            all_cust_colours = ['#D2FADF', '#9FBDA9', '79A387', '#5E7064', '#4D5C52', '#455249', '#3C473F']
            for column in pie_columns:
                if column != 'married':
                    all_customers_df[column] = all_customers_df[column].replace({False: 'Not subscribed',
                                                                                 True: 'Subscribed'})
                elif column == 'married':
                    all_customers_df[column] = all_customers_df[column].replace(
                        {False: 'Not married', True: 'Married'})
            for column in pie_columns:
                fig = make_subplots(rows=1, cols=1, specs=[[{"type": "pie"}]])
                fig.add_trace(go.Pie(
                    values=all_customers_df[column].value_counts().values,
                    labels=all_customers_df[column].value_counts().index,
                    marker=dict(colors=all_cust_colours),
                    hovertemplate='<b>Number of customers</b>: %{value} <extra></extra>',
                    legendgroup=1
                ),
                    row=1, col=1)
                figs.append(fig)

            col = [colours[1]]
            fig_geo = px.scatter_mapbox(all_customers_df, lat="latitude", lon="longitude", custom_data=["population"],
                                        zoom=4.15,
                                        center={'lat': 37.4, 'lon': -119}, opacity=0.7,
                                        color_discrete_sequence=col)
            fig_geo.update_layout(mapbox_accesstoken=
                                  'pk.eyJ1IjoiYW5zbGEiLCJhIjoiY2xkbmU5cG5iMGlobjNudDZhZzc1NzJubiJ9.CAU3T2DiIemshmPHuO6LSA',
                                  margin=dict(l=0, r=0, t=0, b=0))
            fig_geo.update_layout(paper_bgcolor='black')
            fig_geo.update_traces(hovertemplate='<b>Population</b>: %{customdata[0]}<extra></extra>')
            fig_geo.update_layout(title='Geographical distribution')

        titles = ["Satisfaction score", "Customer lifetime value", "Number of referrals", 'Tenure in months',
                  'Average long-distance charges per month', 'Average GB downloaded per month',
                  'Monthly charges', 'Total long-distance charges', 'Total charges',
                  'Total extra data charges', 'Total refunds', 'Age',
                  'Phone service', 'Multiple lines', 'Premium support', 'TV streams',
                  'Movie streams', 'Music streams', 'Internet type', 'Online security', 'Online backup',
                  'Unlimited data', 'Offer', 'Contract', 'Paperless billing', 'Payment method', 'Gender',
                  'Marital status', 'Number of dependents'
                  ]
        x_axes = ['Scores', 'Lifetime value (USD)', 'Number of referrals', 'Months of tenure',
                  'Avg monthly long-distance charges (USD)', 'GB',
                  'Monthly charges (USD)', 'Total long-distance charges (USD)', 'Total charges (USD)',
                  'Total extra data charges (USD)', 'Total refunds (USD)', 'Years'
                  ]
        histogram_num = 0
        for fig, title in zip(figs, titles):
            if histogram_num < 12:
                fig.update_layout(
                    title=title, xaxis_title=x_axes[histogram_num], yaxis_title="% of customers",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    bargap=0.1
                )
                histogram_num += 1
            else:
                fig.update_layout(
                    title=title,
                    legend_tracegroupgap=50
                )

        figs.append(fig_geo)

        html_labels = ['satisfaction_histogram', 'cltv', 'referrals', 'tenure_months',
                       'avg_ld_month', 'avg_gb_month',
                       'monthly', 'total_ld', 'total_charges',
                       'total_extra_data', 'refunds', 'age',
                       'phone_service', 'multiple_lines', 'premium_tech_support',
                       'streaming_tv', 'streaming_movies', 'streaming_music', 'internet_type', 'online_security',
                       'online_backup', 'unlimited_data', 'offer', 'contract', 'paperless', 'payment', 'gender',
                       'married', 'dependents', 'geo']
        for fig, html_label in zip(figs, html_labels):
            fig.update_layout(
                font=dict(size=10, family='Monaco'), template='plotly_dark', height=350, margin=dict(t=30, b=30, r=20),
            )
            html_render = fig.to_html(full_html=False)
            context[html_label] = html_render

        return render(request, 'my_app/home.html', context)
    else:
        return redirect('login')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            if 'username' in form.errors:
                messages.error(request, form.errors['username'])
            if 'email' in form.errors:
                messages.error(request, form.errors['email'])
            if 'password1' in form.errors:
                messages.error(request, form.errors['password1'])
            if 'password2' in form.errors:
                messages.error(request, form.errors['password2'])
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form, 'new_user': True})


@login_required()
def search(request):
    customer_data = None
    alert_message = None

    if request.method == 'POST':
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        customer_number = request.POST['customer_number'].strip()

        if not first_name or not last_name or not customer_number:
            alert_message = "Please fill out all fields."
            messages.error(request, alert_message)
        else:
            if not first_name.isalpha() and not (not first_name):
                alert_message = "First name should contain only letters."
                messages.error(request, alert_message)
            if not last_name.isalpha() and not not last_name:
                alert_message = "Last name should contain only letters."
                messages.error(request, alert_message)
            if not customer_number.isdigit() and not not customer_number:
                alert_message = "Customer number should contain only digits."
                messages.error(request, alert_message)
            elif first_name.isalpha() and last_name.isalpha() and customer_number.isdigit():
                try:
                    customer_personal_data = CustomerPersonalData.objects.get(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name,
                        customer_number__exact=customer_number
                    )
                    if request.user.is_superuser:
                        customer_data = CustomerData.objects.get(customer_personal_data=customer_personal_data)
                    else:
                        assigned_customers = CustomerData.objects.filter(user=request.user)
                        if assigned_customers.filter(customer_personal_data=customer_personal_data).exists():
                            customer_data = assigned_customers.get(customer_personal_data=customer_personal_data)
                        else:
                            first_assigned = assigned_customers.first()
                            last_assigned = assigned_customers.last()
                            alert_message = f"The customer you are searching for is not accessible in your view. Your assigned customers are {first_assigned.pk} to {last_assigned.pk}."
                            messages.error(request, alert_message)
                except CustomerPersonalData.DoesNotExist:
                    alert_message = "Customer not found. Please try again."
                    messages.error(request, alert_message)

    return render(request, 'my_app/search.html', {'customer_data': customer_data, 'alert_message': alert_message})


@csrf_exempt
@login_required()
def submit_support_request(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)

        if form.is_valid():
            problem = form.cleaned_data['problem']
            occurrence = form.cleaned_data['occurrence']
            additional_info = form.cleaned_data['additional_info']

            support_request = SupportRequest.objects.create(
                user=request.user,
                problem=problem,
                occurrence=occurrence,
                additional_info=additional_info
            )
            support_request_id = support_request.id

            if not problem or not occurrence:
                response = {'status': 'error', 'message': 'Please fill out problem and occurrence.'}
            else:
                message_body = (
                    f"User: {request.user.username} ({request.user.email})\n"
                    f"Date: {support_request.submission_time}\n"
                    f"Problem description: {problem}\n\n"
                    f"Occurrence:\n{occurrence}\n\n"
                    f"Additional info:\n{additional_info}"
                )

                subject = f'Support request number {support_request_id}'
                from_email = 'aslabukho@edu.hse.ru'
                to_emails = [settings.ADMIN_EMAIL]

                send_email(subject, message_body, from_email, to_emails)

                response = {'status': 'success', 'message': 'Your support request has been submitted successfully!'}

        else:
            response = {'status': 'error',
                        'message': 'There was an error submitting your support request. Please try again.'}

    else:
        form = SupportForm()
        return render(request, 'my_app/submit_support.html', {'form': form})

    return JsonResponse(response)


def support_form(request):
    support_form = SupportForm()
    return render(request, 'my_app/support_form.html', {'support_form': support_form})


def support_request_submitted(request, support_request_id):
    return render(request, 'my_app/support_request_submitted.html', {'support_request_id': support_request_id})


@login_required()
def ai_insights(request):
    user = request.user
    current_directory = os.path.dirname(os.path.abspath(__file__))
    model_churn_file_path = os.path.join(current_directory, 'churn_model.cbm')
    cat_features = ['offer', 'internet_type', 'contract', 'payment_method', 'gender']
    numeric = ['satisfaction_score', 'cltv', 'number_of_referrals', 'tenure_in_months',
               'avg_monthly_long_distance_charges', 'avg_monthly_gb_download', 'monthly_charge',
               'total_charges', 'total_refunds', 'total_extra_data_charges', 'total_long_distance_charges',
               'population', 'latitude', 'longitude', 'age', 'number_of_dependents']
    model_churn = CatBoostClassifier()
    model_churn.load_model(model_churn_file_path)
    users_predictions = []

    upsell_file_path = os.path.join(current_directory, 'upsell_model.sav')
    model_upsell = joblib.load(upsell_file_path)

    if request.method == 'POST':
        insight_type = request.POST.get('insight_type', None)
        if insight_type == 'churn_insights':
            if not user.is_superuser:
                user_customers = CustomerData.objects.filter(user=user)
                user_customers_df = pd.DataFrame.from_records(user_customers.values())
                features_test = user_customers_df.drop(['id', 'user_id',
                                                        'customer_personal_data_id'], axis=1)

                scaler_churn_file_path = os.path.join(current_directory, 'scaler.bin')
                scaler = joblib.load(scaler_churn_file_path)

                features_test[numeric] = scaler.transform(features_test[numeric])

                predictions = model_churn.predict(features_test)
                for prediction, id in zip(predictions, user_customers_df['customer_personal_data_id']):
                    customer_data = CustomerPersonalData.objects.get(id=id)
                    users_predictions.append({
                        'name': customer_data.first_name,
                        'surname': customer_data.last_name,
                        'customer_number': customer_data.customer_number,
                        'prediction': prediction,
                        'prediction_type': 'churn'
                    })

            else:
                all_customers = CustomerData.objects.all()
                all_customers_df = pd.DataFrame.from_records(all_customers.values())

                features_test = all_customers_df.drop(['id', 'user_id',
                                                       'customer_personal_data_id'], axis=1)

                scaler_file_path = os.path.join(current_directory, 'scaler.bin')
                scaler = joblib.load(scaler_file_path)

                features_test[numeric] = scaler.transform(features_test[numeric])

                predictions = model_churn.predict(features_test)
                for prediction, id in zip(predictions, all_customers_df['customer_personal_data_id']):
                    customer_data = CustomerPersonalData.objects.get(id=id)
                    users_predictions.append({
                        'name': customer_data.first_name,
                        'surname': customer_data.last_name,
                        'customer_number': customer_data.customer_number,
                        'prediction': prediction,
                        'prediction_type': 'churn'
                    })

        elif insight_type == 'upsell_insights':
            if not user.is_superuser:
                user_customers = CustomerData.objects.filter(user=user)
                user_customers_df = pd.DataFrame.from_records(user_customers.values())
                features_test = user_customers_df.drop(['id', 'user_id',
                                                        'customer_personal_data_id'], axis=1)

                scaler_upsell_file_path = os.path.join(current_directory, 'upsell_scaler.bin')
                scaler = joblib.load(scaler_upsell_file_path)

                dummy_columns = ['satisfaction_score', 'cltv', 'number_of_referrals', 'tenure_in_months',
                                 'phone_service', 'avg_monthly_long_distance_charges', 'multiple_lines',
                                 'avg_monthly_gb_download', 'online_security', 'online_backup',
                                 'premium_tech_support', 'streaming_tv', 'streaming_movies',
                                 'streaming_music', 'unlimited_data', 'paperless_billing',
                                 'monthly_charge', 'total_charges', 'total_refunds',
                                 'total_extra_data_charges', 'total_long_distance_charges', 'population',
                                 'latitude', 'longitude', 'age', 'married', 'number_of_dependents',
                                 'offer_Offer A', 'offer_Offer B', 'offer_Offer C', 'offer_Offer D',
                                 'offer_Offer E', 'internet_type_DSL', 'internet_type_Fiber Optic',
                                 'internet_type_None', 'contract_One Year', 'contract_Two Year',
                                 'payment_method_Credit Card', 'payment_method_Mailed Check', 'gender_Male']

                features_test = pd.get_dummies(features_test, drop_first=True)
                index = 0
                for column in dummy_columns:
                    if column not in features_test.columns:
                        features_test.insert(index, column, 0)
                    index += 1

                features_test[numeric] = scaler.transform(features_test[numeric])

                predictions = model_upsell.predict(features_test)
                predictions = pd.Series(predictions).map({True: 1, False: 0})
                for prediction, id in zip(predictions, user_customers_df['customer_personal_data_id']):
                    customer_data = CustomerPersonalData.objects.get(id=id)
                    users_predictions.append({
                        'name': customer_data.first_name,
                        'surname': customer_data.last_name,
                        'customer_number': customer_data.customer_number,
                        'prediction': prediction,
                        'prediction_type': 'upsell'
                    })

            else:
                all_customers = CustomerData.objects.all()
                all_customers_df = pd.DataFrame.from_records(all_customers.values())

                features_test = all_customers_df.drop(['id', 'user_id',
                                                       'customer_personal_data_id'], axis=1)

                scaler_upsell_file_path = os.path.join(current_directory, 'upsell_scaler.bin')
                scaler = joblib.load(scaler_upsell_file_path)

                features_test = pd.get_dummies(features_test, drop_first=True)

                features_test[numeric] = scaler.transform(features_test[numeric])

                predictions = model_upsell.predict(features_test)
                predictions = pd.Series(predictions).map({True: 1, False: 0})
                for prediction, id in zip(predictions, all_customers_df['customer_personal_data_id']):
                    customer_data = CustomerPersonalData.objects.get(id=id)
                    users_predictions.append({
                        'name': customer_data.first_name,
                        'surname': customer_data.last_name,
                        'customer_number': customer_data.customer_number,
                        'prediction': prediction,
                        'prediction_type': 'upsell'
                    })
    context = {
        'users_predictions': users_predictions
    }

    return render(request, 'my_app/ai_insights.html', context)
