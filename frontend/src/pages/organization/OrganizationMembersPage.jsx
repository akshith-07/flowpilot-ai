/**
 * OrganizationMembersPage Component
 * Manage organization members, roles, and invitations
 */

import { useEffect, useState } from 'react';
import {
  UserGroupIcon,
  PlusIcon,
  TrashIcon,
  PaperAirplaneIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Card, { CardHeader, CardTitle, CardDescription, CardBody } from '@/components/ui/Card';
import Modal, { ConfirmModal } from '@/components/ui/Modal';
import DataTable from '@/components/ui/DataTable';
import { FormInput, FormSelect } from '@/components/ui/Form';
import organizationService from '@/services/organizationService';
import { formatDate, formatRelativeTime } from '@/utils/formatters';
import toast from 'react-hot-toast';

/**
 * OrganizationMembersPage Component
 */
export default function OrganizationMembersPage() {
  const [members, setMembers] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [removeMemberModalOpen, setRemoveMemberModalOpen] = useState(false);
  const [cancelInviteModalOpen, setCancelInviteModalOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);
  const [selectedInvitation, setSelectedInvitation] = useState(null);

  const [inviteForm, setInviteForm] = useState({
    email: '',
    role: 'member',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [membersResponse, invitationsResponse] = await Promise.all([
        organizationService.getMembers(),
        organizationService.getInvitations(),
      ]);

      setMembers(membersResponse.data || []);
      setInvitations(invitationsResponse.data || []);
    } catch (error) {
      toast.error(error.message || 'Failed to fetch members');
    } finally {
      setLoading(false);
    }
  };

  const handleInviteMember = async () => {
    try {
      await organizationService.inviteMember(inviteForm);
      toast.success('Invitation sent successfully');
      setInviteModalOpen(false);
      setInviteForm({ email: '', role: 'member' });
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to send invitation');
    }
  };

  const handleRemoveMember = async () => {
    try {
      await organizationService.removeMember(selectedMember.id);
      toast.success('Member removed successfully');
      setRemoveMemberModalOpen(false);
      setSelectedMember(null);
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to remove member');
    }
  };

  const handleCancelInvitation = async () => {
    try {
      await organizationService.cancelInvitation(selectedInvitation.id);
      toast.success('Invitation cancelled');
      setCancelInviteModalOpen(false);
      setSelectedInvitation(null);
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to cancel invitation');
    }
  };

  const handleResendInvitation = async (invitationId) => {
    try {
      await organizationService.resendInvitation(invitationId);
      toast.success('Invitation resent');
    } catch (error) {
      toast.error(error.message || 'Failed to resend invitation');
    }
  };

  const handleUpdateRole = async (memberId, newRole) => {
    try {
      await organizationService.updateMemberRole(memberId, newRole);
      toast.success('Role updated successfully');
      fetchData();
    } catch (error) {
      toast.error(error.message || 'Failed to update role');
    }
  };

  const getRoleBadge = (role) => {
    const roleConfig = {
      owner: { variant: 'primary', label: 'Owner' },
      admin: { variant: 'success', label: 'Admin' },
      manager: { variant: 'info', label: 'Manager' },
      member: { variant: 'secondary', label: 'Member' },
      viewer: { variant: 'secondary', label: 'Viewer' },
    };
    const config = roleConfig[role] || roleConfig.member;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const memberColumns = [
    {
      key: 'user',
      label: 'Member',
      render: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center font-medium">
              {(row.name || row.email || 'U').charAt(0).toUpperCase()}
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-medium text-gray-900">{row.name || 'Unknown'}</span>
            <span className="text-sm text-gray-500">{row.email}</span>
          </div>
        </div>
      ),
    },
    {
      key: 'role',
      label: 'Role',
      render: (value, row) => (
        <FormSelect
          value={value}
          onChange={(e) => handleUpdateRole(row.id, e.target.value)}
          options={[
            { label: 'Owner', value: 'owner' },
            { label: 'Admin', value: 'admin' },
            { label: 'Manager', value: 'manager' },
            { label: 'Member', value: 'member' },
            { label: 'Viewer', value: 'viewer' },
          ]}
          className="w-40"
        />
      ),
    },
    {
      key: 'joined_at',
      label: 'Joined',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'last_active_at',
      label: 'Last Active',
      render: (value) => (
        <span className="text-sm text-gray-500">
          {value ? formatRelativeTime(value) : 'Never'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row) => (
        <Button
          variant="ghost"
          size="sm"
          leftIcon={TrashIcon}
          onClick={(e) => {
            e.stopPropagation();
            setSelectedMember(row);
            setRemoveMemberModalOpen(true);
          }}
          className="text-error-600 hover:text-error-700"
          title="Remove"
          disabled={row.role === 'owner'}
        />
      ),
    },
  ];

  const invitationColumns = [
    {
      key: 'email',
      label: 'Email',
      render: (value) => (
        <span className="text-sm font-medium text-gray-900">{value}</span>
      ),
    },
    {
      key: 'role',
      label: 'Role',
      render: (value) => getRoleBadge(value),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => (
        <Badge variant="warning">{value || 'Pending'}</Badge>
      ),
    },
    {
      key: 'created_at',
      label: 'Invited',
      render: (value) => (
        <span className="text-sm text-gray-500">{formatRelativeTime(value)}</span>
      ),
    },
    {
      key: 'expires_at',
      label: 'Expires',
      render: (value) => (
        <span className="text-sm text-gray-500">
          {value ? formatRelativeTime(value) : 'Never'}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row) => (
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            leftIcon={PaperAirplaneIcon}
            onClick={(e) => {
              e.stopPropagation();
              handleResendInvitation(row.id);
            }}
            title="Resend"
          />
          <Button
            variant="ghost"
            size="sm"
            leftIcon={XMarkIcon}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedInvitation(row);
              setCancelInviteModalOpen(true);
            }}
            className="text-error-600 hover:text-error-700"
            title="Cancel"
          />
        </div>
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team Members</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your organization members and their roles
          </p>
        </div>
        <Button
          leftIcon={PlusIcon}
          onClick={() => setInviteModalOpen(true)}
        >
          Invite Member
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardBody>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="w-8 h-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Members</p>
                <p className="text-2xl font-bold text-gray-900">{members.length}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <PaperAirplaneIcon className="w-8 h-8 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pending Invitations</p>
                <p className="text-2xl font-bold text-gray-900">{invitations.length}</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="w-8 h-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Members</p>
                <p className="text-2xl font-bold text-gray-900">
                  {members.filter((m) => m.last_active_at).length}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Members Table */}
      <Card>
        <CardHeader>
          <CardTitle>Members</CardTitle>
          <CardDescription>
            People who have access to your organization
          </CardDescription>
        </CardHeader>
        <CardBody>
          <DataTable
            data={members}
            columns={memberColumns}
            searchable
            pagination
            emptyMessage="No members yet"
          />
        </CardBody>
      </Card>

      {/* Pending Invitations */}
      {invitations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pending Invitations</CardTitle>
            <CardDescription>
              Invitations that are waiting to be accepted
            </CardDescription>
          </CardHeader>
          <CardBody>
            <DataTable
              data={invitations}
              columns={invitationColumns}
              emptyMessage="No pending invitations"
            />
          </CardBody>
        </Card>
      )}

      {/* Invite Member Modal */}
      <Modal
        isOpen={inviteModalOpen}
        onClose={() => setInviteModalOpen(false)}
        title="Invite Team Member"
      >
        <div className="space-y-4">
          <FormInput
            label="Email Address"
            type="email"
            required
            placeholder="member@example.com"
            value={inviteForm.email}
            onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
          />
          <FormSelect
            label="Role"
            required
            value={inviteForm.role}
            onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
            options={[
              { label: 'Admin', value: 'admin' },
              { label: 'Manager', value: 'manager' },
              { label: 'Member', value: 'member' },
              { label: 'Viewer', value: 'viewer' },
            ]}
          />
          <div className="text-sm text-gray-500">
            An invitation email will be sent with a link to join the organization.
          </div>
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setInviteModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleInviteMember} leftIcon={PaperAirplaneIcon}>
            Send Invitation
          </Button>
        </div>
      </Modal>

      {/* Remove Member Confirmation Modal */}
      <ConfirmModal
        isOpen={removeMemberModalOpen}
        onClose={() => setRemoveMemberModalOpen(false)}
        onConfirm={handleRemoveMember}
        title="Remove Member"
        message={`Are you sure you want to remove ${selectedMember?.name || selectedMember?.email} from the organization?`}
        confirmText="Remove"
        variant="danger"
      />

      {/* Cancel Invitation Confirmation Modal */}
      <ConfirmModal
        isOpen={cancelInviteModalOpen}
        onClose={() => setCancelInviteModalOpen(false)}
        onConfirm={handleCancelInvitation}
        title="Cancel Invitation"
        message={`Are you sure you want to cancel the invitation for ${selectedInvitation?.email}?`}
        confirmText="Cancel Invitation"
        variant="danger"
      />
    </div>
  );
}
