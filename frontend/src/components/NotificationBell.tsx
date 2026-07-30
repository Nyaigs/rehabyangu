import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BellIcon as BellOutline } from '@heroicons/react/24/outline';
import { BellIcon as BellSolid } from '@heroicons/react/24/solid';
import { CheckIcon } from '@heroicons/react/24/outline';
import api from '../api/client';

const fetchNotifications = async () => {
  const { data } = await api.get('/notifications/');
  return data;
};

const markAsRead = async (id: number) => {
  await api.patch(`/notifications/${id}/mark-read/`);
};

const NotificationBell: React.FC = () => {
  const [showDropdown, setShowDropdown] = useState(false);
  const { data: notifications, refetch } = useQuery({
    queryKey: ['notifications'],
    queryFn: fetchNotifications,
    refetchInterval: 60000,
  });

  const unreadCount = notifications?.filter((n: any) => !n.is_read).length || 0;

  const mutation = useMutation({
    mutationFn: markAsRead,
    onSuccess: () => {
      refetch();
    },
  });

  const handleMarkRead = (id: number) => {
    mutation.mutate(id);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-1.5 rounded-full hover:bg-gray-100 transition-colors duration-200 focus:outline-none"
      >
        {unreadCount > 0 ? (
          <BellSolid className="w-4 h-4 text-yellow-500" />
        ) : (
          <BellOutline className="w-4 h-4 text-gray-600" />
        )}
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] rounded-full min-w-[1rem] h-4 flex items-center justify-center font-bold border border-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-lg z-50 max-h-[70vh] overflow-hidden border border-gray-200">
          <div className="p-2.5 border-b border-gray-200 flex justify-between items-center bg-gray-50">
            <span className="text-xs font-semibold text-gray-700">Notifications</span>
            {unreadCount > 0 && (
              <span className="text-[10px] text-red-500 font-medium">{unreadCount} unread</span>
            )}
          </div>
          <div className="overflow-y-auto max-h-72">
            {notifications?.length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-xs">No notifications</div>
            ) : (
              notifications?.map((n: any) => (
                <div
                  key={n.id}
                  className={`p-2.5 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                    n.is_read ? 'bg-white' : 'bg-blue-50'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium text-gray-800">{n.title}</div>
                      <div className="text-[11px] text-gray-600 mt-0.5 break-words">{n.message}</div>
                      <div className="text-[10px] text-gray-400 mt-1">
                        {new Date(n.created_at).toLocaleString()}
                      </div>
                    </div>
                    {!n.is_read && (
                      <button
                        onClick={() => handleMarkRead(n.id)}
                        className="flex-shrink-0 p-0.5 text-blue-600 hover:bg-blue-100 rounded-full transition-colors"
                        title="Mark as read"
                      >
                        <CheckIcon className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="p-1.5 border-t border-gray-200 text-center text-[10px] text-gray-400 bg-gray-50">
            {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up'}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
