/**
 * Not Found Page
 * 404 error page
 */

import { Link } from 'react-router-dom';
import { HomeIcon } from '@heroicons/react/24/outline';
import { Button } from '@components/ui';
import { ROUTES } from '@constants';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary-600">404</h1>
        <h2 className="mt-4 text-3xl font-bold text-gray-900">Page not found</h2>
        <p className="mt-2 text-gray-600">
          Sorry, we couldn't find the page you're looking for.
        </p>
        <div className="mt-8">
          <Link to={ROUTES.HOME}>
            <Button leftIcon={<HomeIcon className="h-5 w-5" />}>
              Go back home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
