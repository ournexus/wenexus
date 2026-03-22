CREATE TYPE "public"."deliverable_format" AS ENUM('markdown', 'html', 'json', 'jsx');--> statement-breakpoint
CREATE TYPE "public"."deliverable_status" AS ENUM('generating', 'ready', 'exported', 'failed');--> statement-breakpoint
CREATE TYPE "public"."deliverable_type" AS ENUM('report', 'article', 'script', 'checklist', 'social', 'observation_card');--> statement-breakpoint
CREATE TYPE "public"."discussion_depth" AS ENUM('quick', 'balanced', 'deep');--> statement-breakpoint
CREATE TYPE "public"."expert_role" AS ENUM('economist', 'technologist', 'ethicist', 'fact_checker', 'custom');--> statement-breakpoint
CREATE TYPE "public"."expert_stance" AS ENUM('supportive', 'critical', 'neutral', 'analytical');--> statement-breakpoint
CREATE TYPE "public"."message_role" AS ENUM('expert', 'host', 'participant', 'system', 'fact_checker');--> statement-breakpoint
CREATE TYPE "public"."observation_card_stance" AS ENUM('supportive', 'critical', 'neutral');--> statement-breakpoint
CREATE TYPE "public"."session_mode" AS ENUM('autopilot', 'host', 'participant');--> statement-breakpoint
CREATE TYPE "public"."session_status" AS ENUM('initializing', 'fact_checking', 'discussing', 'concluding', 'completed');--> statement-breakpoint
CREATE TYPE "public"."topic_status" AS ENUM('draft', 'active', 'discussing', 'completed', 'archived');--> statement-breakpoint
CREATE TYPE "public"."topic_type" AS ENUM('debate', 'brainstorm', 'analysis', 'exploration');--> statement-breakpoint
CREATE TYPE "public"."topic_visibility" AS ENUM('public', 'private');--> statement-breakpoint
CREATE TABLE "account" (
	"id" text PRIMARY KEY NOT NULL,
	"account_id" text NOT NULL,
	"provider_id" text NOT NULL,
	"user_id" text NOT NULL,
	"access_token" text,
	"refresh_token" text,
	"id_token" text,
	"access_token_expires_at" timestamp,
	"refresh_token_expires_at" timestamp,
	"scope" text,
	"password" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL
);
--> statement-breakpoint
CREATE TABLE "ai_task" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"media_type" text NOT NULL,
	"provider" text NOT NULL,
	"model" text NOT NULL,
	"prompt" text NOT NULL,
	"options" text,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp,
	"task_id" text,
	"task_info" text,
	"task_result" text,
	"cost_credits" integer DEFAULT 0 NOT NULL,
	"scene" text DEFAULT '' NOT NULL,
	"credit_id" text
);
--> statement-breakpoint
CREATE TABLE "apikey" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"key" text NOT NULL,
	"title" text NOT NULL,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp
);
--> statement-breakpoint
CREATE TABLE "chat" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"model" text NOT NULL,
	"provider" text NOT NULL,
	"title" text DEFAULT '' NOT NULL,
	"parts" text NOT NULL,
	"metadata" text,
	"content" text
);
--> statement-breakpoint
CREATE TABLE "chat_message" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"chat_id" text NOT NULL,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"role" text NOT NULL,
	"parts" text NOT NULL,
	"metadata" text,
	"model" text NOT NULL,
	"provider" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "config" (
	"name" text NOT NULL,
	"value" text,
	CONSTRAINT "config_name_unique" UNIQUE("name")
);
--> statement-breakpoint
CREATE TABLE "credit" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"user_email" text,
	"order_no" text,
	"subscription_no" text,
	"transaction_no" text NOT NULL,
	"transaction_type" text NOT NULL,
	"transaction_scene" text,
	"credits" integer NOT NULL,
	"remaining_credits" integer DEFAULT 0 NOT NULL,
	"description" text,
	"expires_at" timestamp,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp,
	"consumed_detail" text,
	"metadata" text,
	CONSTRAINT "credit_transaction_no_unique" UNIQUE("transaction_no")
);
--> statement-breakpoint
CREATE TABLE "deliverable" (
	"id" text PRIMARY KEY NOT NULL,
	"session_id" text NOT NULL,
	"topic_id" text NOT NULL,
	"user_id" text NOT NULL,
	"type" "deliverable_type" NOT NULL,
	"title" text,
	"content" text,
	"format" "deliverable_format" DEFAULT 'markdown',
	"status" "deliverable_status" NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "discussion_message" (
	"id" text PRIMARY KEY NOT NULL,
	"session_id" text NOT NULL,
	"expert_id" text,
	"user_id" text,
	"role" "message_role" NOT NULL,
	"content" text NOT NULL,
	"thread_ref" text,
	"citations" jsonb,
	"status" text DEFAULT 'active' NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "discussion_session" (
	"id" text PRIMARY KEY NOT NULL,
	"topic_id" text NOT NULL,
	"user_id" text NOT NULL,
	"status" "session_status" NOT NULL,
	"mode" "session_mode" DEFAULT 'autopilot' NOT NULL,
	"consensus_level" integer DEFAULT 0,
	"expert_ids" jsonb,
	"is_private" boolean DEFAULT false NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"completed_at" timestamp
);
--> statement-breakpoint
CREATE TABLE "expert" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"role" "expert_role" NOT NULL,
	"avatar" text,
	"stance" "expert_stance",
	"description" text,
	"system_prompt" text,
	"is_builtin" boolean DEFAULT false NOT NULL,
	"created_by_user_id" text,
	"status" text DEFAULT 'active' NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "observation_card" (
	"id" text PRIMARY KEY NOT NULL,
	"topic_id" text NOT NULL,
	"expert_id" text,
	"session_id" text,
	"title" text NOT NULL,
	"content" text NOT NULL,
	"stance" "observation_card_stance",
	"likes" integer DEFAULT 0 NOT NULL,
	"status" text DEFAULT 'active' NOT NULL,
	"cover_image" text,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "order" (
	"id" text PRIMARY KEY NOT NULL,
	"order_no" text NOT NULL,
	"user_id" text NOT NULL,
	"user_email" text,
	"status" text NOT NULL,
	"amount" integer NOT NULL,
	"currency" text NOT NULL,
	"product_id" text,
	"payment_type" text,
	"payment_interval" text,
	"payment_provider" text NOT NULL,
	"payment_session_id" text,
	"checkout_info" text NOT NULL,
	"checkout_result" text,
	"payment_result" text,
	"discount_code" text,
	"discount_amount" integer,
	"discount_currency" text,
	"payment_email" text,
	"payment_amount" integer,
	"payment_currency" text,
	"paid_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp,
	"description" text,
	"product_name" text,
	"subscription_id" text,
	"subscription_result" text,
	"checkout_url" text,
	"callback_url" text,
	"credits_amount" integer,
	"credits_valid_days" integer,
	"plan_name" text,
	"payment_product_id" text,
	"invoice_id" text,
	"invoice_url" text,
	"subscription_no" text,
	"transaction_id" text,
	"payment_user_name" text,
	"payment_user_id" text,
	CONSTRAINT "order_order_no_unique" UNIQUE("order_no")
);
--> statement-breakpoint
CREATE TABLE "permission" (
	"id" text PRIMARY KEY NOT NULL,
	"code" text NOT NULL,
	"resource" text NOT NULL,
	"action" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	CONSTRAINT "permission_code_unique" UNIQUE("code")
);
--> statement-breakpoint
CREATE TABLE "post" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"parent_id" text,
	"slug" text NOT NULL,
	"type" text NOT NULL,
	"title" text,
	"description" text,
	"image" text,
	"content" text,
	"categories" text,
	"tags" text,
	"author_name" text,
	"author_image" text,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp,
	"sort" integer DEFAULT 0 NOT NULL,
	CONSTRAINT "post_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "role" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"sort" integer DEFAULT 0 NOT NULL,
	CONSTRAINT "role_name_unique" UNIQUE("name")
);
--> statement-breakpoint
CREATE TABLE "role_permission" (
	"id" text PRIMARY KEY NOT NULL,
	"role_id" text NOT NULL,
	"permission_id" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp
);
--> statement-breakpoint
CREATE TABLE "session" (
	"id" text PRIMARY KEY NOT NULL,
	"expires_at" timestamp NOT NULL,
	"token" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"ip_address" text,
	"user_agent" text,
	"user_id" text NOT NULL,
	CONSTRAINT "session_token_unique" UNIQUE("token")
);
--> statement-breakpoint
CREATE TABLE "subscription" (
	"id" text PRIMARY KEY NOT NULL,
	"subscription_no" text NOT NULL,
	"user_id" text NOT NULL,
	"user_email" text,
	"status" text NOT NULL,
	"payment_provider" text NOT NULL,
	"subscription_id" text NOT NULL,
	"subscription_result" text,
	"product_id" text,
	"description" text,
	"amount" integer,
	"currency" text,
	"interval" text,
	"interval_count" integer,
	"trial_period_days" integer,
	"current_period_start" timestamp,
	"current_period_end" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp,
	"plan_name" text,
	"billing_url" text,
	"product_name" text,
	"credits_amount" integer,
	"credits_valid_days" integer,
	"payment_product_id" text,
	"payment_user_id" text,
	"canceled_at" timestamp,
	"canceled_end_at" timestamp,
	"canceled_reason" text,
	"canceled_reason_type" text,
	CONSTRAINT "subscription_subscription_no_unique" UNIQUE("subscription_no")
);
--> statement-breakpoint
CREATE TABLE "taxonomy" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"parent_id" text,
	"slug" text NOT NULL,
	"type" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"image" text,
	"icon" text,
	"status" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"deleted_at" timestamp,
	"sort" integer DEFAULT 0 NOT NULL,
	CONSTRAINT "taxonomy_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "topic" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"title" text NOT NULL,
	"description" text,
	"type" "topic_type" NOT NULL,
	"status" "topic_status" NOT NULL,
	"visibility" "topic_visibility" DEFAULT 'public' NOT NULL,
	"deliverable_type" "deliverable_type",
	"cover_image" text,
	"tags" jsonb,
	"consensus_level" integer DEFAULT 0,
	"participant_count" integer DEFAULT 0,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"deleted_at" timestamp
);
--> statement-breakpoint
CREATE TABLE "user" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"email" text NOT NULL,
	"email_verified" boolean DEFAULT false NOT NULL,
	"image" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"utm_source" text DEFAULT '' NOT NULL,
	"ip" text DEFAULT '' NOT NULL,
	"locale" text DEFAULT '' NOT NULL,
	CONSTRAINT "user_email_unique" UNIQUE("email")
);
--> statement-breakpoint
CREATE TABLE "user_preference" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"preferred_experts" jsonb,
	"preferred_output_formats" jsonb,
	"discussion_depth" "discussion_depth" DEFAULT 'balanced',
	"background_info" jsonb,
	"onboarding_completed" boolean DEFAULT false NOT NULL,
	"metadata" jsonb,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "user_role" (
	"id" text PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"role_id" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"expires_at" timestamp
);
--> statement-breakpoint
CREATE TABLE "verification" (
	"id" text PRIMARY KEY NOT NULL,
	"identifier" text NOT NULL,
	"value" text NOT NULL,
	"expires_at" timestamp NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "account" ADD CONSTRAINT "account_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "ai_task" ADD CONSTRAINT "ai_task_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "apikey" ADD CONSTRAINT "apikey_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "chat" ADD CONSTRAINT "chat_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "chat_message" ADD CONSTRAINT "chat_message_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "chat_message" ADD CONSTRAINT "chat_message_chat_id_chat_id_fk" FOREIGN KEY ("chat_id") REFERENCES "public"."chat"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "credit" ADD CONSTRAINT "credit_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "deliverable" ADD CONSTRAINT "deliverable_session_id_discussion_session_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."discussion_session"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "deliverable" ADD CONSTRAINT "deliverable_topic_id_topic_id_fk" FOREIGN KEY ("topic_id") REFERENCES "public"."topic"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "deliverable" ADD CONSTRAINT "deliverable_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "discussion_message" ADD CONSTRAINT "discussion_message_session_id_discussion_session_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."discussion_session"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "discussion_message" ADD CONSTRAINT "discussion_message_expert_id_expert_id_fk" FOREIGN KEY ("expert_id") REFERENCES "public"."expert"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "discussion_message" ADD CONSTRAINT "discussion_message_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "discussion_session" ADD CONSTRAINT "discussion_session_topic_id_topic_id_fk" FOREIGN KEY ("topic_id") REFERENCES "public"."topic"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "discussion_session" ADD CONSTRAINT "discussion_session_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "expert" ADD CONSTRAINT "expert_created_by_user_id_user_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "public"."user"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "observation_card" ADD CONSTRAINT "observation_card_topic_id_topic_id_fk" FOREIGN KEY ("topic_id") REFERENCES "public"."topic"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "observation_card" ADD CONSTRAINT "observation_card_expert_id_expert_id_fk" FOREIGN KEY ("expert_id") REFERENCES "public"."expert"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "observation_card" ADD CONSTRAINT "observation_card_session_id_discussion_session_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."discussion_session"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "order" ADD CONSTRAINT "order_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "post" ADD CONSTRAINT "post_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "role_permission" ADD CONSTRAINT "role_permission_role_id_role_id_fk" FOREIGN KEY ("role_id") REFERENCES "public"."role"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "role_permission" ADD CONSTRAINT "role_permission_permission_id_permission_id_fk" FOREIGN KEY ("permission_id") REFERENCES "public"."permission"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "session" ADD CONSTRAINT "session_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "subscription" ADD CONSTRAINT "subscription_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "taxonomy" ADD CONSTRAINT "taxonomy_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "topic" ADD CONSTRAINT "topic_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_preference" ADD CONSTRAINT "user_preference_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_role" ADD CONSTRAINT "user_role_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "user_role" ADD CONSTRAINT "user_role_role_id_role_id_fk" FOREIGN KEY ("role_id") REFERENCES "public"."role"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "idx_account_user_id" ON "account" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "idx_account_provider_account" ON "account" USING btree ("provider_id","account_id");--> statement-breakpoint
CREATE INDEX "idx_ai_task_user_media_type" ON "ai_task" USING btree ("user_id","media_type");--> statement-breakpoint
CREATE INDEX "idx_ai_task_media_type_status" ON "ai_task" USING btree ("media_type","status");--> statement-breakpoint
CREATE INDEX "idx_apikey_user_status" ON "apikey" USING btree ("user_id","status");--> statement-breakpoint
CREATE INDEX "idx_apikey_key_status" ON "apikey" USING btree ("key","status");--> statement-breakpoint
CREATE INDEX "idx_chat_user_status" ON "chat" USING btree ("user_id","status");--> statement-breakpoint
CREATE INDEX "idx_chat_message_chat_id" ON "chat_message" USING btree ("chat_id","status");--> statement-breakpoint
CREATE INDEX "idx_chat_message_user_id" ON "chat_message" USING btree ("user_id","status");--> statement-breakpoint
CREATE INDEX "idx_credit_consume_fifo" ON "credit" USING btree ("user_id","status","transaction_type","remaining_credits","expires_at");--> statement-breakpoint
CREATE INDEX "idx_credit_order_no" ON "credit" USING btree ("order_no");--> statement-breakpoint
CREATE INDEX "idx_credit_subscription_no" ON "credit" USING btree ("subscription_no");--> statement-breakpoint
CREATE INDEX "idx_deliverable_session" ON "deliverable" USING btree ("session_id","type");--> statement-breakpoint
CREATE INDEX "idx_deliverable_user_type" ON "deliverable" USING btree ("user_id","type","status");--> statement-breakpoint
CREATE INDEX "idx_deliverable_topic" ON "deliverable" USING btree ("topic_id");--> statement-breakpoint
CREATE INDEX "idx_discussion_message_session" ON "discussion_message" USING btree ("session_id","created_at");--> statement-breakpoint
CREATE INDEX "idx_discussion_message_thread" ON "discussion_message" USING btree ("thread_ref");--> statement-breakpoint
CREATE INDEX "idx_discussion_session_topic" ON "discussion_session" USING btree ("topic_id","status");--> statement-breakpoint
CREATE INDEX "idx_discussion_session_user" ON "discussion_session" USING btree ("user_id","status");--> statement-breakpoint
CREATE INDEX "idx_expert_role_status" ON "expert" USING btree ("role","status");--> statement-breakpoint
CREATE INDEX "idx_expert_builtin" ON "expert" USING btree ("is_builtin");--> statement-breakpoint
CREATE INDEX "idx_observation_card_topic" ON "observation_card" USING btree ("topic_id","status");--> statement-breakpoint
CREATE INDEX "idx_observation_card_created_at" ON "observation_card" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_order_user_status_payment_type" ON "order" USING btree ("user_id","status","payment_type");--> statement-breakpoint
CREATE INDEX "idx_order_transaction_provider" ON "order" USING btree ("transaction_id","payment_provider");--> statement-breakpoint
CREATE INDEX "idx_order_created_at" ON "order" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_permission_resource_action" ON "permission" USING btree ("resource","action");--> statement-breakpoint
CREATE INDEX "idx_post_type_status" ON "post" USING btree ("type","status");--> statement-breakpoint
CREATE INDEX "idx_role_status" ON "role" USING btree ("status");--> statement-breakpoint
CREATE INDEX "idx_role_permission_role_permission" ON "role_permission" USING btree ("role_id","permission_id");--> statement-breakpoint
CREATE INDEX "idx_session_user_expires" ON "session" USING btree ("user_id","expires_at");--> statement-breakpoint
CREATE INDEX "idx_subscription_user_status_interval" ON "subscription" USING btree ("user_id","status","interval");--> statement-breakpoint
CREATE INDEX "idx_subscription_provider_id" ON "subscription" USING btree ("subscription_id","payment_provider");--> statement-breakpoint
CREATE INDEX "idx_subscription_created_at" ON "subscription" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_taxonomy_type_status" ON "taxonomy" USING btree ("type","status");--> statement-breakpoint
CREATE INDEX "idx_topic_user_status" ON "topic" USING btree ("user_id","status");--> statement-breakpoint
CREATE INDEX "idx_topic_status_visibility" ON "topic" USING btree ("status","visibility");--> statement-breakpoint
CREATE INDEX "idx_topic_created_at" ON "topic" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_user_name" ON "user" USING btree ("name");--> statement-breakpoint
CREATE INDEX "idx_user_created_at" ON "user" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_user_preference_user" ON "user_preference" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "idx_user_role_user_expires" ON "user_role" USING btree ("user_id","expires_at");--> statement-breakpoint
CREATE INDEX "idx_verification_identifier" ON "verification" USING btree ("identifier");
