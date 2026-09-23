from django.urls import path

from .views import AdmissionsReportView, CensusReportView, DischargesReportView, OccupancyReportView, OutstandingReportView, RevenueReportView

urlpatterns = [
    path('reports/occupancy/', OccupancyReportView.as_view()),
    path('reports/census/', CensusReportView.as_view()),
    path('reports/admissions/', AdmissionsReportView.as_view()),
    path('reports/discharges/', DischargesReportView.as_view()),
    path('reports/revenue/', RevenueReportView.as_view()),
    path('reports/outstanding/', OutstandingReportView.as_view()),
]
