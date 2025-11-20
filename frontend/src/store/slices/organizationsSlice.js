import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import organizationService from '@/services/organizationService';

// Async thunks
export const fetchOrganization = createAsyncThunk(
  'organizations/fetch',
  async (_, { rejectWithValue }) => {
    try {
      const response = await organizationService.getOrganization();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch organization');
    }
  }
);

export const updateOrganization = createAsyncThunk(
  'organizations/update',
  async (data, { rejectWithValue }) => {
    try {
      const response = await organizationService.updateOrganization(data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update organization');
    }
  }
);

export const fetchMembers = createAsyncThunk(
  'organizations/fetchMembers',
  async (params, { rejectWithValue }) => {
    try {
      const response = await organizationService.getMembers(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch members');
    }
  }
);

export const inviteMember = createAsyncThunk(
  'organizations/inviteMember',
  async (inviteData, { rejectWithValue }) => {
    try {
      const response = await organizationService.inviteMember(inviteData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to invite member');
    }
  }
);

export const removeMember = createAsyncThunk(
  'organizations/removeMember',
  async (memberId, { rejectWithValue }) => {
    try {
      await organizationService.removeMember(memberId);
      return memberId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to remove member');
    }
  }
);

export const updateMemberRole = createAsyncThunk(
  'organizations/updateMemberRole',
  async ({ memberId, role }, { rejectWithValue }) => {
    try {
      const response = await organizationService.updateMemberRole(memberId, role);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update member role');
    }
  }
);

export const fetchRoles = createAsyncThunk(
  'organizations/fetchRoles',
  async (_, { rejectWithValue }) => {
    try {
      const response = await organizationService.getRoles();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch roles');
    }
  }
);

export const fetchInvitations = createAsyncThunk(
  'organizations/fetchInvitations',
  async (_, { rejectWithValue }) => {
    try {
      const response = await organizationService.getInvitations();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch invitations');
    }
  }
);

export const cancelInvitation = createAsyncThunk(
  'organizations/cancelInvitation',
  async (invitationId, { rejectWithValue }) => {
    try {
      await organizationService.cancelInvitation(invitationId);
      return invitationId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to cancel invitation');
    }
  }
);

export const fetchAPIKeys = createAsyncThunk(
  'organizations/fetchAPIKeys',
  async (_, { rejectWithValue }) => {
    try {
      const response = await organizationService.getAPIKeys();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch API keys');
    }
  }
);

export const createAPIKey = createAsyncThunk(
  'organizations/createAPIKey',
  async (data, { rejectWithValue }) => {
    try {
      const response = await organizationService.createAPIKey(data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create API key');
    }
  }
);

export const revokeAPIKey = createAsyncThunk(
  'organizations/revokeAPIKey',
  async (keyId, { rejectWithValue }) => {
    try {
      await organizationService.revokeAPIKey(keyId);
      return keyId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to revoke API key');
    }
  }
);

// Initial state
const initialState = {
  organization: null,
  members: [],
  roles: [],
  invitations: [],
  apiKeys: [],
  loading: false,
  error: null,
  memberPagination: {
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,
  },
};

// Slice
const organizationsSlice = createSlice({
  name: 'organizations',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setMemberPagination: (state, action) => {
      state.memberPagination = { ...state.memberPagination, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch organization
      .addCase(fetchOrganization.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrganization.fulfilled, (state, action) => {
        state.loading = false;
        state.organization = action.payload;
      })
      .addCase(fetchOrganization.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update organization
      .addCase(updateOrganization.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateOrganization.fulfilled, (state, action) => {
        state.loading = false;
        state.organization = action.payload;
      })
      .addCase(updateOrganization.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch members
      .addCase(fetchMembers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMembers.fulfilled, (state, action) => {
        state.loading = false;
        state.members = action.payload.results || action.payload;
        state.memberPagination = {
          page: action.payload.page || 1,
          pageSize: action.payload.page_size || 10,
          total: action.payload.count || action.payload.length,
          totalPages: action.payload.total_pages || 1,
        };
      })
      .addCase(fetchMembers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Invite member
      .addCase(inviteMember.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(inviteMember.fulfilled, (state, action) => {
        state.loading = false;
        state.invitations.unshift(action.payload);
      })
      .addCase(inviteMember.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Remove member
      .addCase(removeMember.fulfilled, (state, action) => {
        state.members = state.members.filter((m) => m.id !== action.payload);
      })

      // Update member role
      .addCase(updateMemberRole.fulfilled, (state, action) => {
        const index = state.members.findIndex((m) => m.id === action.payload.id);
        if (index !== -1) {
          state.members[index] = action.payload;
        }
      })

      // Fetch roles
      .addCase(fetchRoles.fulfilled, (state, action) => {
        state.roles = action.payload;
      })

      // Fetch invitations
      .addCase(fetchInvitations.fulfilled, (state, action) => {
        state.invitations = action.payload;
      })

      // Cancel invitation
      .addCase(cancelInvitation.fulfilled, (state, action) => {
        state.invitations = state.invitations.filter((i) => i.id !== action.payload);
      })

      // Fetch API keys
      .addCase(fetchAPIKeys.fulfilled, (state, action) => {
        state.apiKeys = action.payload;
      })

      // Create API key
      .addCase(createAPIKey.fulfilled, (state, action) => {
        state.apiKeys.unshift(action.payload);
      })

      // Revoke API key
      .addCase(revokeAPIKey.fulfilled, (state, action) => {
        const key = state.apiKeys.find((k) => k.id === action.payload);
        if (key) {
          key.is_active = false;
        }
      });
  },
});

export const { clearError, setMemberPagination } = organizationsSlice.actions;

export default organizationsSlice.reducer;
