/**
 * UserSecurityPage Component
 * User security settings with password change, MFA, and active sessions
 */

import { useEffect, useState } from 'react';
import {
  LockClosedIcon,
  ShieldCheckIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  XMarkIcon,
  KeyIcon,
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Card, { CardHeader, CardTitle, CardDescription, CardBody } from '@/components/ui/Card';
import Modal, { ConfirmModal } from '@/components/ui/Modal';
import DataTable from '@/components/ui/DataTable';
import { FormInput } from '@/components/ui/Form';
import userService from '@/services/userService';
import { formatDate, formatRelativeTime } from '@/utils/formatters';
import toast from 'react-hot-toast';

/**
 * UserSecurityPage Component
 */
export default function UserSecurityPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [changePasswordModalOpen, setChangePasswordModalOpen] = useState(false);
  const [enable2FAModalOpen, setEnable2FAModalOpen] = useState(false);
  const [disable2FAModalOpen, setDisable2FAModalOpen] = useState(false);
  const [revokeSessionModalOpen, setRevokeSessionModalOpen] = useState(false);
  const [backupCodesModalOpen, setBackupCodesModalOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [backupCodes, setBackupCodes] = useState([]);

  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [verify2FACode, setVerify2FACode] = useState('');
  const [disable2FAPassword, setDisable2FAPassword] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sessionsResponse, userResponse] = await Promise.all([
        userService.getSessions(),
        userService.getCurrentUser(),
      ]);

      setSessions(sessionsResponse.data || []);
      setMfaEnabled(userResponse.data.mfa_enabled || false);
    } catch (error) {
      toast.error(error.message || 'Failed to fetch security data');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    try {
      await userService.changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
      });
      toast.success('Password changed successfully');
      setChangePasswordModalOpen(false);
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      toast.error(error.message || 'Failed to change password');
    }
  };

  const handleEnable2FA = async () => {
    try {
      const response = await userService.enable2FA();
      setQrCode(response.data.qr_code);
      setBackupCodes(response.data.backup_codes || []);
    } catch (error) {
      toast.error(error.message || 'Failed to enable 2FA');
    }
  };

  const handleVerify2FA = async () => {
    try {
      await userService.verify2FA(verify2FACode);
      toast.success('Two-factor authentication enabled successfully');
      setEnable2FAModalOpen(false);
      setQrCode(null);
      setVerify2FACode('');
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Invalid verification code');
    }
  };

  const handleDisable2FA = async () => {
    try {
      await userService.disable2FA(disable2FAPassword);
      toast.success('Two-factor authentication disabled');
      setDisable2FAModalOpen(false);
      setDisable2FAPassword('');
      setMfaEnabled(false);
    } catch (error) {
      toast.error(error.message || 'Failed to disable 2FA');
    }
  };

  const handleRevokeSession = async () => {
    try {
      await userService.revokeSession(selectedSession.id);
      toast.success('Session revoked successfully');
      setRevokeSessionModalOpen(false);
      setSelectedSession(null);
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to revoke session');
    }
  };

  const handleShowBackupCodes = async () => {
    try {
      const response = await userService.getBackupCodes();
      setBackupCodes(response.data.codes || []);
      setBackupCodesModalOpen(true);
    } catch (error) {
      toast.error(error.message || 'Failed to fetch backup codes');
    }
  };

  const handleRegenerateBackupCodes = async () => {
    try {
      const response = await userService.regenerateBackupCodes();
      setBackupCodes(response.data.codes || []);
      toast.success('Backup codes regenerated');
    } catch (error) {
      toast.error(error.message || 'Failed to regenerate backup codes');
    }
  };

  const getDeviceIcon = (deviceType) => {
    if (deviceType?.toLowerCase().includes('mobile')) {
      return DevicePhoneMobileIcon;
    }
    return ComputerDesktopIcon;
  };

  const sessionColumns = [
    {
      key: 'device',
      label: 'Device',
      render: (value, row) => {
        const DeviceIcon = getDeviceIcon(row.device_type);
        return (
          <div className="flex items-center space-x-3">
            <DeviceIcon className="w-5 h-5 text-gray-400" />
            <div className="flex flex-col">
              <span className="font-medium text-gray-900">
                {row.device_name || row.user_agent || 'Unknown Device'}
              </span>
              <span className="text-xs text-gray-500">
                {row.ip_address} • {row.location || 'Unknown location'}
              </span>
            </div>
          </div>
        );
      },
    },
    {
      key: 'is_current',
      label: 'Status',
      render: (value) =>
        value ? (
          <Badge variant="success">Current Session</Badge>
        ) : (
          <Badge variant="secondary">Active</Badge>
        ),
    },
    {
      key: 'last_active_at',
      label: 'Last Active',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'created_at',
      label: 'Started',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row) =>
        !row.is_current && (
          <Button
            variant="ghost"
            size="sm"
            leftIcon={XMarkIcon}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedSession(row);
              setRevokeSessionModalOpen(true);
            }}
            className="text-error-600 hover:text-error-700"
            title="Revoke"
          />
        ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Security Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account security and authentication settings
        </p>
      </div>

      {/* Password */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <LockClosedIcon className="w-5 h-5 text-gray-400" />
                <CardTitle>Password</CardTitle>
              </div>
              <CardDescription>
                Change your password to keep your account secure
              </CardDescription>
            </div>
            <Button onClick={() => setChangePasswordModalOpen(true)}>
              Change Password
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          <div className="text-sm text-gray-600">
            <p>Last changed: Never</p>
            <p className="mt-2">Password requirements:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>At least 8 characters long</li>
              <li>Contains uppercase and lowercase letters</li>
              <li>Contains at least one number</li>
              <li>Contains at least one special character</li>
            </ul>
          </div>
        </CardBody>
      </Card>

      {/* Two-Factor Authentication */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <ShieldCheckIcon className="w-5 h-5 text-gray-400" />
                <CardTitle>Two-Factor Authentication (2FA)</CardTitle>
              </div>
              <CardDescription>
                Add an extra layer of security to your account
              </CardDescription>
            </div>
            {mfaEnabled ? (
              <div className="flex items-center space-x-3">
                <Badge variant="success" dot>
                  Enabled
                </Badge>
                <Button variant="outline" onClick={handleShowBackupCodes}>
                  Backup Codes
                </Button>
                <Button variant="danger" onClick={() => setDisable2FAModalOpen(true)}>
                  Disable 2FA
                </Button>
              </div>
            ) : (
              <Button
                onClick={() => {
                  setEnable2FAModalOpen(true);
                  handleEnable2FA();
                }}
              >
                Enable 2FA
              </Button>
            )}
          </div>
        </CardHeader>
        <CardBody>
          <div className="text-sm text-gray-600">
            {mfaEnabled ? (
              <p>
                Two-factor authentication is enabled. You will be prompted for a verification
                code when logging in from a new device.
              </p>
            ) : (
              <p>
                Two-factor authentication adds an extra layer of security to your account by
                requiring a verification code in addition to your password.
              </p>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Active Sessions */}
      <Card>
        <CardHeader>
          <CardTitle>Active Sessions</CardTitle>
          <CardDescription>
            Manage devices where you are currently logged in
          </CardDescription>
        </CardHeader>
        <CardBody>
          <DataTable
            data={sessions}
            columns={sessionColumns}
            emptyMessage="No active sessions"
          />
        </CardBody>
      </Card>

      {/* Security Audit Log */}
      <Card>
        <CardHeader>
          <CardTitle>Security Activity</CardTitle>
          <CardDescription>
            Recent security-related activities on your account
          </CardDescription>
        </CardHeader>
        <CardBody>
          <div className="text-center py-12">
            <KeyIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-sm text-gray-500">No recent security activity</p>
          </div>
        </CardBody>
      </Card>

      {/* Change Password Modal */}
      <Modal
        isOpen={changePasswordModalOpen}
        onClose={() => setChangePasswordModalOpen(false)}
        title="Change Password"
      >
        <div className="space-y-4">
          <FormInput
            label="Current Password"
            type="password"
            required
            value={passwordForm.old_password}
            onChange={(e) =>
              setPasswordForm({ ...passwordForm, old_password: e.target.value })
            }
            placeholder="Enter current password"
          />
          <FormInput
            label="New Password"
            type="password"
            required
            value={passwordForm.new_password}
            onChange={(e) =>
              setPasswordForm({ ...passwordForm, new_password: e.target.value })
            }
            placeholder="Enter new password"
          />
          <FormInput
            label="Confirm New Password"
            type="password"
            required
            value={passwordForm.confirm_password}
            onChange={(e) =>
              setPasswordForm({ ...passwordForm, confirm_password: e.target.value })
            }
            placeholder="Confirm new password"
          />
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setChangePasswordModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleChangePassword}>Change Password</Button>
        </div>
      </Modal>

      {/* Enable 2FA Modal */}
      <Modal
        isOpen={enable2FAModalOpen}
        onClose={() => {
          setEnable2FAModalOpen(false);
          setQrCode(null);
          setVerify2FACode('');
        }}
        title="Enable Two-Factor Authentication"
        size="lg"
      >
        <div className="space-y-4">
          {qrCode ? (
            <>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-4">
                  Scan this QR code with your authenticator app
                </p>
                <div className="inline-block p-4 bg-white border border-gray-200 rounded-lg">
                  <img src={qrCode} alt="QR Code" className="w-48 h-48" />
                </div>
              </div>
              <FormInput
                label="Verification Code"
                required
                value={verify2FACode}
                onChange={(e) => setVerify2FACode(e.target.value)}
                placeholder="Enter 6-digit code"
              />
              {backupCodes.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-yellow-800 mb-2">
                    Save these backup codes in a safe place:
                  </p>
                  <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                    {backupCodes.map((code, index) => (
                      <div key={index} className="bg-white px-2 py-1 rounded">
                        {code}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-sm text-gray-600">Generating QR code...</p>
            </div>
          )}
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button
            variant="outline"
            onClick={() => {
              setEnable2FAModalOpen(false);
              setQrCode(null);
              setVerify2FACode('');
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleVerify2FA} disabled={!verify2FACode}>
            Verify & Enable
          </Button>
        </div>
      </Modal>

      {/* Disable 2FA Modal */}
      <Modal
        isOpen={disable2FAModalOpen}
        onClose={() => setDisable2FAModalOpen(false)}
        title="Disable Two-Factor Authentication"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Disabling two-factor authentication will make your account less secure. Please
            enter your password to confirm.
          </p>
          <FormInput
            label="Password"
            type="password"
            required
            value={disable2FAPassword}
            onChange={(e) => setDisable2FAPassword(e.target.value)}
            placeholder="Enter your password"
          />
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setDisable2FAModalOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDisable2FA}>
            Disable 2FA
          </Button>
        </div>
      </Modal>

      {/* Backup Codes Modal */}
      <Modal
        isOpen={backupCodesModalOpen}
        onClose={() => setBackupCodesModalOpen(false)}
        title="Backup Codes"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Use these codes to access your account if you lose access to your authenticator
            app. Each code can only be used once.
          </p>
          <div className="grid grid-cols-2 gap-2 font-mono text-sm">
            {backupCodes.map((code, index) => (
              <div
                key={index}
                className="bg-gray-50 px-3 py-2 rounded border border-gray-200"
              >
                {code}
              </div>
            ))}
          </div>
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setBackupCodesModalOpen(false)}>
            Close
          </Button>
          <Button onClick={handleRegenerateBackupCodes}>Regenerate Codes</Button>
        </div>
      </Modal>

      {/* Revoke Session Confirmation Modal */}
      <ConfirmModal
        isOpen={revokeSessionModalOpen}
        onClose={() => setRevokeSessionModalOpen(false)}
        onConfirm={handleRevokeSession}
        title="Revoke Session"
        message="Are you sure you want to revoke this session? The device will be logged out immediately."
        confirmText="Revoke Session"
        variant="danger"
      />
    </div>
  );
}
