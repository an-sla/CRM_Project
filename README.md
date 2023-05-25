# Analytical CRM Simulation Project


<br>

**This project is aimed at building an analytical CRM web-application utilising insights gained from Machine Learning.**
<br></br>
## Use Cases and Objectives

There are two use-cases which will be analysed based on customer behaviour: **churn** and **cross-sell / up-sell**.

**The holistic aims of the project include:**
- Analysing appropriate datasets fitting the use cases described above;
- Building, training, validating, and testing ML models in order to attain the best possible metrics selected for each use-case;
- Using ML-model output and data as content for a CRM web-application built using Django;
- Populating the web-app with dashboards based on data in order to simulate a real CRM system;
- Hosting the web-app as to simulate an independent service.
<br></br>

## Django Web-app

The web-application is contained in the `/DjangoCRM/` directory, including settings, views, templates, forms and styles. It is hosted on pythonanywhere.com and accessible through [this link](http://crmwebapp.pythonanywhere.com). 

The web-app is conceptualised as a site with user logins, with multiple regular users and one Django super-user. Each user (a potential 'Relationship Manager' in the simulated company) has access to a cohort of 20 customers, who are linked with the user account upon sign-up.
The following login details may be used:

1.	Super-user name: admin <br> Password: 113326as
2.	User name: jane_doe <br> Password: paDte9-sykhez-bepmex

User credentials are saved upon sign-up to the Django SQLite database. Users may only sign up with a `telco` (corporate) email account; every user's password must also contain 8 alphanumeric characters. In case of errors, alerts appear on the sign-up screen.
Through these credentials, the inner web-app service may be accessed.
It includes the following menus (subpages):
- Dashboard
- Search
- AI Insights
- Support

The Dashboard view provides dashboards of each user's cohort performance in comparison with average values across the entire customer database. The super-user view only contains database averages.
<br>The Search view allows to search for individual users. In order to test the capabilities of the function, one may try searching for John Backus with the customer number 100000.
<br>The AI insights view generates ML predictions for the churn and cross-sell / up-sell use cases for the given cohort (with all database customer predictions again being displayed for the super-user).
<br>Finally, the Support view enables users to send support / helpline requests to a specially dedicated Gmail account, with request numbers and details being saved to the Django database. Mailjet's API is used in order to forward these email messages.



## Data Analysis 

This project currently contains the data and Jupyter Notebook for the churn use case and the cross-sell / up-sell use case. Originally inspired by the `Telco Churn` project in the [Bootcamp directory](https://github.com/an-sla/BootcampProjects), this analysis is based on a new enriched Telco Churn dataset by IBM, made available via Kaggle. The client is a Telecommunications company in the USA, and its clients use mobile and internet services. The business problem involves predicting whether they will churn, i.e., leave the company; in addition, the cross-sell / up-sell use case includes a classification problem of whether users may be offered a device security plan product.

The `enriched_churn.ipynb` file with the preliminary analysis (EDA) and ML pipeline is stored in the `/EnrichedTelco` directory. The second use case applies its models to the same data, stored and cleaned as the `clean_data.csv` file, with the ML component of the cross-sell / up-sell use case being provided in the `upsell.ipynb` file.

The original raw data is composed of 5 tables in the `.xlsx` format, which are stored in the `/EnrichedTelco/data_archive` sub-directory. Table and data descriptions are available in the first Jupyter Notebook for churn. For further information on the dataset see the **'Licence'** subsection of this file.
<br></br>

## Potentail Improvements and Updates

This app may be further updates with GitHub webhooks in order to automatically update pythonanywhere.com hosting at every `git push` command.
<br>
The Support form may also be improved, since its style is currently incomplete, and its alerts appear in a different location to the rest of the project. All JavaScript code may also be separated into appropriate files.
<br>
The Search page functionality may also be extended to include user (or super-user) editing of database data.
<br>
Further ML applications and data insights may also be possible.

![LastUpdate](https://img.shields.io/badge/Latest%20Update-25.05.23-green)


## License

This project uses the GNU General Public License 3.0.

### Churn and Cross-sell / Up-sell Dataset:

The dataset is originally linked to IBM's Cognos Analytics 11.1.3+ Version Sample, made available via Kaggle. All data is property of IBM and/or its original author.

More information on the dataset can be found [here](https://www.kaggle.com/datasets/ylchang/telco-customer-churn-1113?select=Telco_customer_churn.xlsx), with attribution to IBM.
<br></br>

## Contributors

Anastasia / [an-sla](https://github.com/an-sla)

[![Linkedin](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/anastasia-slabucho-21b9b219b/)
