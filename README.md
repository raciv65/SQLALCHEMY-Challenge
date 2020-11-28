# SQLALCHEMY-Challenge

In this repository, we work with the SQLAlchemy module as well as queries.

The exercise consisted of analyzing the climate of Hawaii to plan a vacation in the place.

Using the precipitation and temperature information, an analysis was carried out to have a rain and temperature projection that will allow you to plan your vacation with better weather conditions.

The base has different stations and information from 2010 to 2017. For the analysis, was used data from the last twelve months was used for the analysis. Also, the queries dependeable of the planification trip.

## Bonus Analysis

Derived from the fact that the series is in the same location but in different seasons of the year, a paired test is used.

First, the test is performed to determine if the series has a normal distribution. Based on the p-value (in both cases less than 0.05), the null hypothesis is rejected, so the series does not have a normal distribution. Therefore a nonparametric test is performed.

Based on the nonparametric paired test, the p-value is less than 0.05. Thus the null hypothesis is rejected, and we argue that the average temperature in June is significantly different from the average temperature in December.
