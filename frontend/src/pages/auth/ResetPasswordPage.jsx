/**
 * Reset Password Page
 * Set new password after receiving reset link
 */

import { useNavigate, useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useForm } from 'react-hook-form';
import { LockClosedIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { Button, Input } from '@components/ui';
import { ROUTES } from '@constants';
import { confirmPasswordReset, selectAuthLoading } from '@store/slices/authSlice';

export default function ResetPasswordPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const loading = useSelector(selectAuthLoading);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm();

  const password = watch('password');

  const onSubmit = async (data) => {
    try {
      await dispatch(confirmPasswordReset({
        token,
        password: data.password,
      })).unwrap();
      toast.success('Password reset successful! Please login.');
      navigate(ROUTES.LOGIN);
    } catch (err) {
      toast.error(err || 'Failed to reset password. Please try again.');
    }
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Reset your password</h2>
        <p className="mt-2 text-sm text-gray-600">
          Enter your new password below
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Input
          label="New Password"
          type="password"
          placeholder="••••••••"
          leftIcon={<LockClosedIcon className="h-5 w-5" />}
          error={errors.password?.message}
          helperText="Must be at least 8 characters"
          {...register('password', {
            required: 'Password is required',
            minLength: {
              value: 8,
              message: 'Password must be at least 8 characters',
            },
          })}
        />

        <Input
          label="Confirm New Password"
          type="password"
          placeholder="••••••••"
          leftIcon={<LockClosedIcon className="h-5 w-5" />}
          error={errors.confirm_password?.message}
          {...register('confirm_password', {
            required: 'Please confirm your password',
            validate: (value) =>
              value === password || 'Passwords do not match',
          })}
        />

        <Button
          type="submit"
          fullWidth
          loading={loading}
        >
          Reset Password
        </Button>
      </form>
    </div>
  );
}
