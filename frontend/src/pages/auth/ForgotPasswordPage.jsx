/**
 * Forgot Password Page
 * Request password reset email
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useForm } from 'react-hook-form';
import { EnvelopeIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { Button, Input } from '@components/ui';
import { ROUTES } from '@constants';
import { requestPasswordReset, selectAuthLoading } from '@store/slices/authSlice';

export default function ForgotPasswordPage() {
  const dispatch = useDispatch();
  const loading = useSelector(selectAuthLoading);
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    try {
      await dispatch(requestPasswordReset(data.email)).unwrap();
      setSubmitted(true);
      toast.success('Password reset email sent!');
    } catch (err) {
      toast.error(err || 'Failed to send reset email. Please try again.');
    }
  };

  if (submitted) {
    return (
      <div className="text-center">
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-success-100">
          <svg
            className="h-6 w-6 text-success-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 className="mt-4 text-2xl font-bold text-gray-900">Check your email</h2>
        <p className="mt-2 text-sm text-gray-600">
          We've sent a password reset link to your email address.
        </p>
        <div className="mt-6">
          <Link
            to={ROUTES.LOGIN}
            className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Forgot password?</h2>
        <p className="mt-2 text-sm text-gray-600">
          Enter your email address and we'll send you a link to reset your password
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Input
          label="Email Address"
          type="email"
          placeholder="you@example.com"
          leftIcon={<EnvelopeIcon className="h-5 w-5" />}
          error={errors.email?.message}
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Invalid email address',
            },
          })}
        />

        <Button
          type="submit"
          fullWidth
          loading={loading}
        >
          Send Reset Link
        </Button>

        <div className="text-center">
          <Link
            to={ROUTES.LOGIN}
            className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to login
          </Link>
        </div>
      </form>
    </div>
  );
}
