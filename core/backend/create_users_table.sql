BEGIN;
--
-- Create model User
--
CREATE TABLE "users" ("password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "id" char(32) NOT NULL PRIMARY KEY, "email" varchar(254) NOT NULL UNIQUE, "phone_number" varchar(20) NOT NULL, "bio" text NOT NULL, "avatar" varchar(100) NULL, "date_of_birth" date NULL, "country" varchar(2) NOT NULL, "city" varchar(100) NOT NULL, "user_timezone" varchar(50) NOT NULL, "language" varchar(10) NOT NULL, "theme" varchar(20) NOT NULL, "notifications_enabled" bool NOT NULL, "email_notifications" bool NOT NULL, "is_verified" bool NOT NULL, "verification_token" varchar(100) NOT NULL, "last_password_change" datetime NOT NULL, "require_password_change" bool NOT NULL, "last_activity" datetime NULL, "login_count" integer unsigned NOT NULL CHECK ("login_count" >= 0), "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
CREATE TABLE "users_blocked_users" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "from_user_id" char(32) NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED, "to_user_id" char(32) NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "users_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" char(32) NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "users_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" char(32) NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model UserDevice
--
CREATE TABLE "user_devices" ("id" char(32) NOT NULL PRIMARY KEY, "device_id" varchar(255) NOT NULL UNIQUE, "device_type" varchar(20) NOT NULL, "device_name" varchar(100) NOT NULL, "device_model" varchar(100) NOT NULL, "push_token" text NOT NULL, "last_used" datetime NOT NULL, "created_at" datetime NOT NULL, "is_active" bool NOT NULL, "user_id" char(32) NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model UserNotification
--
CREATE TABLE "user_notifications" ("id" char(32) NOT NULL PRIMARY KEY, "title" varchar(200) NOT NULL, "message" text NOT NULL, "notification_type" varchar(50) NOT NULL, "related_object_type" varchar(50) NOT NULL, "related_object_id" varchar(50) NOT NULL, "created_at" datetime NOT NULL, "read_at" datetime NULL, "is_read" bool NOT NULL, "action_url" varchar(200) NOT NULL, "user_id" char(32) NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model UserProfile
--
CREATE TABLE "user_profiles" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "occupation" varchar(100) NOT NULL, "company" varchar(100) NOT NULL, "website" varchar(200) NOT NULL, "linkedin" varchar(200) NOT NULL, "github" varchar(50) NOT NULL, "default_currency" varchar(3) NOT NULL, "inflation_basket" text NOT NULL CHECK ((JSON_VALID("inflation_basket") OR "inflation_basket" IS NULL)), "recaria_stats" text NOT NULL CHECK ((JSON_VALID("recaria_stats") OR "recaria_stats" IS NULL)), "birlikteyiz_id" varchar(50) NOT NULL, "profile_visibility" varchar(20) NOT NULL, "show_online_status" bool NOT NULL, "total_points" integer unsigned NOT NULL CHECK ("total_points" >= 0), "level" integer unsigned NOT NULL CHECK ("level" >= 0), "achievements" text NOT NULL CHECK ((JSON_VALID("achievements") OR "achievements" IS NULL)), "user_id" char(32) NOT NULL UNIQUE REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create index users_email_4b85f2_idx on field(s) email of model user
--
CREATE INDEX "users_email_4b85f2_idx" ON "users" ("email");
--
-- Create index users_usernam_baeb4b_idx on field(s) username of model user
--
CREATE INDEX "users_usernam_baeb4b_idx" ON "users" ("username");
--
-- Create index users_is_acti_6b2a46_idx on field(s) is_active, is_verified of model user
--
CREATE INDEX "users_is_acti_6b2a46_idx" ON "users" ("is_active", "is_verified");
--
-- Create index user_device_user_id_14e9e9_idx on field(s) user, is_active of model userdevice
--
CREATE INDEX "user_device_user_id_14e9e9_idx" ON "user_devices" ("user_id", "is_active");
--
-- Create index user_device_device__945e98_idx on field(s) device_id of model userdevice
--
CREATE INDEX "user_device_device__945e98_idx" ON "user_devices" ("device_id");
--
-- Create index user_notifi_user_id_ea6762_idx on field(s) user, is_read of model usernotification
--
CREATE INDEX "user_notifi_user_id_ea6762_idx" ON "user_notifications" ("user_id", "is_read");
--
-- Create index user_notifi_created_0a808a_idx on field(s) created_at of model usernotification
--
CREATE INDEX "user_notifi_created_0a808a_idx" ON "user_notifications" ("created_at");
CREATE UNIQUE INDEX "users_blocked_users_from_user_id_to_user_id_61e619cf_uniq" ON "users_blocked_users" ("from_user_id", "to_user_id");
CREATE INDEX "users_blocked_users_from_user_id_6b806754" ON "users_blocked_users" ("from_user_id");
CREATE INDEX "users_blocked_users_to_user_id_0daecbaa" ON "users_blocked_users" ("to_user_id");
CREATE UNIQUE INDEX "users_groups_user_id_group_id_fc7788e8_uniq" ON "users_groups" ("user_id", "group_id");
CREATE INDEX "users_groups_user_id_f500bee5" ON "users_groups" ("user_id");
CREATE INDEX "users_groups_group_id_2f3517aa" ON "users_groups" ("group_id");
CREATE UNIQUE INDEX "users_user_permissions_user_id_permission_id_3b86cbdf_uniq" ON "users_user_permissions" ("user_id", "permission_id");
CREATE INDEX "users_user_permissions_user_id_92473840" ON "users_user_permissions" ("user_id");
CREATE INDEX "users_user_permissions_permission_id_6d08dcd2" ON "users_user_permissions" ("permission_id");
CREATE INDEX "user_devices_user_id_211f69db" ON "user_devices" ("user_id");
CREATE INDEX "user_notifications_user_id_0ac00350" ON "user_notifications" ("user_id");
COMMIT;
