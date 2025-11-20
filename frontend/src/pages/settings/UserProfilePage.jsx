/**
 * UserProfilePage Component
 * User profile settings with personal information and preferences
 */

import { useEffect, useState } from 'react';
import {
  UserCircleIcon,
  BellIcon,
  GlobeAltIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Card, { CardHeader, CardTitle, CardDescription, CardBody } from '@/components/ui/Card';
import { ConfirmModal } from '@/components/ui/Modal';
import { FormInput, FormSelect, FormCheckbox, FormSwitch } from '@/components/ui/Form';
import userService from '@/services/userService';
import toast from 'react-hot-toast';

/**
 * UserProfilePage Component
 */
export default function UserProfilePage() {
  const [user, setUser] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleteAccountModalOpen, setDeleteAccountModalOpen] = useState(false);

  const [profileForm, setProfileForm] = useState({
    name: '',
    email: '',
    timezone: '',
    language: '',
  });

  const [notificationPrefs, setNotificationPrefs] = useState({
    email_notifications: true,
    slack_notifications: false,
    workflow_completed: true,
    workflow_failed: true,
    daily_summary: false,
    weekly_report: false,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [userResponse, prefsResponse] = await Promise.all([
        userService.getCurrentUser(),
        userService.getPreferences(),
      ]);

      setUser(userResponse.data);
      setPreferences(prefsResponse.data);

      setProfileForm({
        name: userResponse.data.name || '',
        email: userResponse.data.email || '',
        timezone: userResponse.data.timezone || '',
        language: userResponse.data.language || '',
      });

      setNotificationPrefs({
        ...notificationPrefs,
        ...prefsResponse.data,
      });
    } catch (error) {
      toast.error(error.message || 'Failed to fetch user data');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      await userService.updateProfile(profileForm);
      toast.success('Profile updated successfully');
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSavePreferences = async () => {
    try {
      setSaving(true);
      await userService.updatePreferences(notificationPrefs);
      toast.success('Preferences updated successfully');
    } catch (error) {
      toast.error(error.message || 'Failed to update preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await userService.updateAvatar(file);
      toast.success('Avatar updated successfully');
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to upload avatar');
    }
  };

  const handleDeleteAccount = async () => {
    toast.error('Account deletion is not implemented yet');
    setDeleteAccountModalOpen(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your personal information and preferences
        </p>
      </div>

      {/* Profile Information */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <UserCircleIcon className="w-5 h-5 text-gray-400" />
            <CardTitle>Profile Information</CardTitle>
          </div>
          <CardDescription>
            Update your personal information and profile picture
          </CardDescription>
        </CardHeader>
        <CardBody>
          <div className="space-y-6">
            {/* Avatar */}
            <div className="flex items-center space-x-6">
              <div className="flex-shrink-0">
                <div className="w-24 h-24 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-3xl font-medium">
                  {(profileForm.name || profileForm.email || 'U').charAt(0).toUpperCase()}
                </div>
              </div>
              <div>
                <input
                  type="file"
                  id="avatar-upload"
                  accept="image/*"
                  className="hidden"
                  onChange={handleAvatarUpload}
                />
                <label htmlFor="avatar-upload">
                  <Button as="span" variant="outline" size="sm">
                    Change Avatar
                  </Button>
                </label>
                <p className="mt-2 text-xs text-gray-500">
                  JPG, PNG or GIF. Max size 2MB.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormInput
                label="Full Name"
                required
                value={profileForm.name}
                onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                placeholder="Enter your name"
              />
              <FormInput
                label="Email Address"
                type="email"
                required
                value={profileForm.email}
                onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                placeholder="your@email.com"
              />
            </div>

            <div className="flex justify-end">
              <Button onClick={handleSaveProfile} loading={saving}>
                Save Profile
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <GlobeAltIcon className="w-5 h-5 text-gray-400" />
            <CardTitle>Preferences</CardTitle>
          </div>
          <CardDescription>
            Configure your timezone and language preferences
          </CardDescription>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <FormSelect
              label="Timezone"
              value={profileForm.timezone}
              onChange={(e) => setProfileForm({ ...profileForm, timezone: e.target.value })}
              options={[
                { label: 'UTC', value: 'UTC' },
                { label: 'America/New_York', value: 'America/New_York' },
                { label: 'America/Chicago', value: 'America/Chicago' },
                { label: 'America/Los_Angeles', value: 'America/Los_Angeles' },
                { label: 'Europe/London', value: 'Europe/London' },
                { label: 'Asia/Tokyo', value: 'Asia/Tokyo' },
              ]}
            />
            <FormSelect
              label="Language"
              value={profileForm.language}
              onChange={(e) => setProfileForm({ ...profileForm, language: e.target.value })}
              options={[
                { label: 'English (US)', value: 'en-US' },
                { label: 'English (UK)', value: 'en-GB' },
                { label: 'Spanish', value: 'es' },
                { label: 'French', value: 'fr' },
                { label: 'German', value: 'de' },
                { label: 'Japanese', value: 'ja' },
              ]}
            />
            <div className="flex justify-end">
              <Button onClick={handleSaveProfile} loading={saving}>
                Save Preferences
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Notification Preferences */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <BellIcon className="w-5 h-5 text-gray-400" />
            <CardTitle>Notification Preferences</CardTitle>
          </div>
          <CardDescription>
            Choose how you want to receive notifications
          </CardDescription>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-900">Notification Channels</h4>
              <FormSwitch
                label="Email Notifications"
                description="Receive notifications via email"
                checked={notificationPrefs.email_notifications}
                onChange={(e) =>
                  setNotificationPrefs({
                    ...notificationPrefs,
                    email_notifications: e.target.checked,
                  })
                }
              />
              <FormSwitch
                label="Slack Notifications"
                description="Receive notifications in Slack"
                checked={notificationPrefs.slack_notifications}
                onChange={(e) =>
                  setNotificationPrefs({
                    ...notificationPrefs,
                    slack_notifications: e.target.checked,
                  })
                }
              />
            </div>

            <div className="border-t border-gray-200 pt-4 space-y-3">
              <h4 className="text-sm font-medium text-gray-900">Workflow Notifications</h4>
              <FormCheckbox
                label="Workflow Completed"
                description="Get notified when a workflow completes successfully"
                checked={notificationPrefs.workflow_completed}
                onChange={(e) =>
                  setNotificationPrefs({
                    ...notificationPrefs,
                    workflow_completed: e.target.checked,
                  })
                }
              />
              <FormCheckbox
                label="Workflow Failed"
                description="Get notified when a workflow fails"
                checked={notificationPrefs.workflow_failed}
                onChange={(e) =>
                  setNotificationPrefs({
                    ...notificationPrefs,
                    workflow_failed: e.target.checked,
                  })
                }
              />
            </div>

            <div className="border-t border-gray-200 pt-4 space-y-3">
              <h4 className="text-sm font-medium text-gray-900">Reports</h4>
              <FormCheckbox
                label="Daily Summary"
                description="Receive a daily summary of your workflow activity"
                checked={notificationPrefs.daily_summary}
                onChange={(e) =>
                  setNotificationPrefs({
                    ...notificationPrefs,
                    daily_summary: e.target.checked,
                  })
                }
              />
              <FormCheckbox
                label="Weekly Report"
                description="Receive a weekly report with detailed analytics"
                checked={notificationPrefs.weekly_report}
                onChange={(e) =>
                  setNotificationPrefs({
                    ...notificationPrefs,
                    weekly_report: e.target.checked,
                  })
                }
              />
            </div>

            <div className="flex justify-end pt-4">
              <Button onClick={handleSavePreferences} loading={saving}>
                Save Notification Preferences
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Danger Zone */}
      <Card className="border-error-200">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <TrashIcon className="w-5 h-5 text-error-600" />
            <CardTitle className="text-error-600">Danger Zone</CardTitle>
          </div>
          <CardDescription>
            Irreversible actions that will affect your account
          </CardDescription>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-gray-900">Delete Account</h4>
                <p className="text-sm text-gray-500 mt-1">
                  Permanently delete your account and all associated data
                </p>
              </div>
              <Button
                variant="danger"
                onClick={() => setDeleteAccountModalOpen(true)}
              >
                Delete Account
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Delete Account Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteAccountModalOpen}
        onClose={() => setDeleteAccountModalOpen(false)}
        onConfirm={handleDeleteAccount}
        title="Delete Account"
        message="Are you sure you want to delete your account? This action cannot be undone. All your data will be permanently deleted."
        confirmText="Delete Account"
        variant="danger"
      />
    </div>
  );
}
