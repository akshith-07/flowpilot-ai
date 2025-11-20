/**
 * Dashboard Layout
 * Main layout for authenticated pages with sidebar and header
 */

import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  HomeIcon,
  CogIcon,
  DocumentTextIcon,
  CircleStackIcon,
  PlayIcon,
  PuzzlePieceIcon,
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';

import { ROUTES, APP_CONFIG } from '@constants';
import { selectUser, logoutUser } from '@store/slices/authSlice';
import { Avatar } from '@components/ui';
import { cn } from '@utils';

const navigation = [
  { name: 'Dashboard', href: ROUTES.DASHBOARD, icon: HomeIcon },
  { name: 'Workflows', href: ROUTES.WORKFLOWS, icon: CogIcon },
  { name: 'Executions', href: ROUTES.EXECUTIONS, icon: PlayIcon },
  { name: 'Connectors', href: ROUTES.CONNECTORS, icon: PuzzlePieceIcon },
  { name: 'Documents', href: ROUTES.DOCUMENTS, icon: DocumentTextIcon },
  { name: 'Analytics', href: ROUTES.ANALYTICS, icon: ChartBarIcon },
];

export default function DashboardLayout({ children, fullWidth = false }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const user = useSelector(selectUser);

  const handleLogout = async () => {
    await dispatch(logoutUser());
    navigate(ROUTES.LOGIN);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <Transition.Root show={sidebarOpen} as={Fragment}>
        <div className="relative z-50 lg:hidden">
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-900/80" onClick={() => setSidebarOpen(false)} />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <div className="relative mr-16 flex w-full max-w-xs flex-1">
                <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4">
                  <div className="flex h-16 shrink-0 items-center justify-between">
                    <span className="text-xl font-bold text-gray-900">{APP_CONFIG.name}</span>
                    <button
                      type="button"
                      className="-m-2.5 p-2.5"
                      onClick={() => setSidebarOpen(false)}
                    >
                      <XMarkIcon className="h-6 w-6 text-gray-700" />
                    </button>
                  </div>
                  <nav className="flex flex-1 flex-col">
                    <ul className="flex flex-1 flex-col gap-y-7">
                      <li>
                        <ul className="-mx-2 space-y-1">
                          {navigation.map((item) => {
                            const isActive = location.pathname.startsWith(item.href);
                            return (
                              <li key={item.name}>
                                <Link
                                  to={item.href}
                                  className={cn(
                                    isActive
                                      ? 'bg-primary-50 text-primary-600'
                                      : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50',
                                    'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                                  )}
                                  onClick={() => setSidebarOpen(false)}
                                >
                                  <item.icon className="h-6 w-6 shrink-0" />
                                  {item.name}
                                </Link>
                              </li>
                            );
                          })}
                        </ul>
                      </li>
                    </ul>
                  </nav>
                </div>
              </div>
            </Transition.Child>
          </div>
        </div>
      </Transition.Root>

      {/* Static sidebar for desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 bg-white px-6 pb-4">
          <div className="flex h-16 shrink-0 items-center">
            <span className="text-xl font-bold text-gray-900">{APP_CONFIG.name}</span>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul className="-mx-2 space-y-1">
                  {navigation.map((item) => {
                    const isActive = location.pathname.startsWith(item.href);
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={cn(
                            isActive
                              ? 'bg-primary-50 text-primary-600'
                              : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors'
                          )}
                        >
                          <item.icon className="h-6 w-6 shrink-0" />
                          {item.name}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top nav */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* User menu */}
              <Menu as="div" className="relative">
                <Menu.Button className="-m-1.5 flex items-center p-1.5 hover:bg-gray-50 rounded-full transition-colors">
                  <Avatar
                    src={user?.avatar}
                    name={user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email}
                    size="sm"
                  />
                  <span className="hidden lg:flex lg:items-center ml-2">
                    <span className="text-sm font-semibold leading-6 text-gray-900">
                      {user?.first_name || user?.email}
                    </span>
                  </span>
                </Menu.Button>
                <Transition
                  as={Fragment}
                  enter="transition ease-out duration-100"
                  enterFrom="transform opacity-0 scale-95"
                  enterTo="transform opacity-100 scale-100"
                  leave="transition ease-in duration-75"
                  leaveFrom="transform opacity-100 scale-100"
                  leaveTo="transform opacity-0 scale-95"
                >
                  <Menu.Items className="absolute right-0 z-10 mt-2.5 w-48 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                    <Menu.Item>
                      {({ active }) => (
                        <Link
                          to={ROUTES.USER_PROFILE}
                          className={cn(
                            active ? 'bg-gray-50' : '',
                            'flex items-center px-3 py-2 text-sm leading-6 text-gray-900'
                          )}
                        >
                          <UserCircleIcon className="mr-3 h-5 w-5 text-gray-400" />
                          Your Profile
                        </Link>
                      )}
                    </Menu.Item>
                    <Menu.Item>
                      {({ active }) => (
                        <Link
                          to={ROUTES.USER_SECURITY}
                          className={cn(
                            active ? 'bg-gray-50' : '',
                            'flex items-center px-3 py-2 text-sm leading-6 text-gray-900'
                          )}
                        >
                          <Cog6ToothIcon className="mr-3 h-5 w-5 text-gray-400" />
                          Settings
                        </Link>
                      )}
                    </Menu.Item>
                    <Menu.Item>
                      {({ active }) => (
                        <Link
                          to={ROUTES.ORGANIZATION_SETTINGS}
                          className={cn(
                            active ? 'bg-gray-50' : '',
                            'flex items-center px-3 py-2 text-sm leading-6 text-gray-900'
                          )}
                        >
                          <CircleStackIcon className="mr-3 h-5 w-5 text-gray-400" />
                          Organization
                        </Link>
                      )}
                    </Menu.Item>
                    <div className="my-1 h-px bg-gray-200" />
                    <Menu.Item>
                      {({ active }) => (
                        <button
                          onClick={handleLogout}
                          className={cn(
                            active ? 'bg-gray-50' : '',
                            'flex w-full items-center px-3 py-2 text-sm leading-6 text-gray-900'
                          )}
                        >
                          <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5 text-gray-400" />
                          Sign out
                        </button>
                      )}
                    </Menu.Item>
                  </Menu.Items>
                </Transition>
              </Menu>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className={cn('py-8', fullWidth ? 'px-0' : 'px-4 sm:px-6 lg:px-8')}>
          {children}
        </main>
      </div>
    </div>
  );
}
