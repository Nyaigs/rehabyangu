import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { UserPlusIcon, PhoneIcon, ArrowRightIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import PatientForm from '../components/PatientForm';
import { EmptyState } from '../components/EmptyState';
import { SkeletonPatientCard } from '../components/Skeleton';

const fetchPatients = async () => {
  const { data } = await api.get('/patients/');
  return data;
};

const Patients: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');
  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['patients'],
    queryFn: fetchPatients,
  });

  const filtered = patients?.filter((p: any) =>
    `${p.first_name} ${p.last_name} ${p.phone}`.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return <SkeletonPatientCard count={3} />;
  if (error) return <div className="text-danger text-sm p-4">Error loading patients.</div>;

  const getAcuityClass = (status: string) => {
    switch (status) {
      case 'active': return 'acuity-rail-solid';
      case 'discharged': return 'acuity-rail-dotted';
      default: return 'acuity-rail-dashed';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <h1 className="text-xl font-bold text-secondary-800">Patients</h1>
          <p className="text-xs text-secondary-500">Manage all patients across your facility</p>
        </div>
        <Button size="sm" onClick={() => setShowForm(true)}>
          <UserPlusIcon className="w-3.5 h-3.5 mr-1.5" /> Add Patient
        </Button>
      </div>

      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-secondary-400" />
        <Input
          type="text"
          placeholder="Search by name or phone..."
          className="pl-9 h-9 text-sm"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {filtered?.length === 0 ? (
        <EmptyState
          title="No patients found"
          description="Start by adding your first patient."
          actionLabel="Add Patient"
          onAction={() => setShowForm(true)}
          iconType="users"
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered?.map((p: any) => (
            <Link
              key={p.id}
              to="/patients/$id"
              params={{ id: String(p.id) }}
              className={`block ${getAcuityClass(p.status)}`}
            >
              <Card className="hover:shadow-card-hover transition-all duration-200 cursor-pointer group">
                <CardContent className="p-3.5 flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-secondary-800 truncate">
                      {p.first_name} {p.last_name}
                    </h3>
                    <div className="flex items-center gap-1 text-xs text-secondary-500 mt-0.5">
                      <PhoneIcon className="w-3 h-3" />
                      <span>{p.phone}</span>
                    </div>
                    {p.status && (
                      <Badge variant={p.status === 'active' ? 'default' : p.status === 'discharged' ? 'destructive' : 'secondary'} className="mt-1.5 text-[10px]">
                        {p.status}
                      </Badge>
                    )}
                  </div>
                  <ArrowRightIcon className="w-3 h-3 text-secondary-300 group-hover:text-primary-600 transition-colors flex-shrink-0 mt-1" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
      {showForm && <PatientForm onClose={() => setShowForm(false)} />}
    </div>
  );
};

export default Patients;
