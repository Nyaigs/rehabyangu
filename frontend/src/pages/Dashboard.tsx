import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { UsersIcon, CalendarDaysIcon, CreditCardIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../api/client';

const fetchStats = async () => {
  const [patientsRes, appointmentsRes, billsRes] = await Promise.all([
    api.get('/patients/'),
    api.get('/appointments/'),
    api.get('/patient-bill/'),
  ]);
  return {
    patients: patientsRes.data,
    appointments: appointmentsRes.data,
    bills: billsRes.data,
  };
};

const Dashboard: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchStats,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  const totalPatients = data?.patients?.length || 0;
  const activePatients = data?.patients?.filter((p: any) => p.status === 'active').length || 0;
  const appointmentsToday = data?.appointments?.filter((a: any) => {
    const today = new Date().toDateString();
    return new Date(a.start_time).toDateString() === today;
  }).length || 0;
  const totalRevenue = data?.bills?.reduce((sum: number, b: any) => sum + parseFloat(b.total_balance || 0), 0) || 0;

  const chartData = [
    { month: 'Jan', admissions: 4, discharges: 2 },
    { month: 'Feb', admissions: 6, discharges: 3 },
    { month: 'Mar', admissions: 8, discharges: 5 },
    { month: 'Apr', admissions: 5, discharges: 4 },
    { month: 'May', admissions: 7, discharges: 6 },
    { month: 'Jun', admissions: 9, discharges: 7 },
  ];

  const kpis = [
    { label: 'Total Patients', value: totalPatients, icon: UsersIcon, trend: '+2 this week' },
    { label: 'Active Admissions', value: activePatients, icon: ArrowTrendingUpIcon, trend: '84% occupancy' },
    { label: 'Appointments Today', value: appointmentsToday, icon: CalendarDaysIcon, trend: '3 remaining' },
    { label: 'Revenue (month)', value: `KES ${totalRevenue.toFixed(0)}`, icon: CreditCardIcon, trend: '+12% vs last month' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-800">Dashboard</h1>
        <p className="text-sm text-secondary-500">Good morning, welcome back.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <Card key={kpi.label} className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-medium text-secondary-500 uppercase tracking-wider">{kpi.label}</p>
                <p className="text-2xl font-bold text-secondary-900 mt-1">{kpi.value}</p>
                <p className="text-xs text-secondary-500 mt-1">{kpi.trend}</p>
              </div>
              <kpi.icon className="w-5 h-5 text-secondary-400" />
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-semibold">Admission Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d3d7db" />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="admissions" stroke="#1d5a70" strokeWidth={2} />
                <Line type="monotone" dataKey="discharges" stroke="#237a57" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-semibold">Revenue Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData.map((d) => ({ month: d.month, revenue: d.admissions * 50000 }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d3d7db" />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#0f2e3d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button>Add Patient</Button>
        <Button variant="outline">Book Appointment</Button>
        <Button variant="outline">Record Vitals</Button>
        <Button variant="secondary">View Reports</Button>
      </div>
    </div>
  );
};

export default Dashboard;
