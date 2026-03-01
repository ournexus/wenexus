/**
 * @module Identity Domain
 * @description 身份域：用户档案、偏好积累、隐私管控
 * @depends shared-kernel (Event Bus)
 * @consumers Discovery, Roundtable, Deliverable 域 (via getUserPreference)
 */

// Types
export type {
  UserPreference,
  UpdateUserPreference,
  UserBackgroundInfo,
  UserIdentity,
} from './types';
export { DiscussionDepth } from './types';

// Services
export {
  getUserPreference,
  updateUserPreference,
  getUserIdentity,
} from './services/user-profile-service';
