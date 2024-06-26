drop database if exists `cset180final`;

create database if not exists `cset180final`;
use `cset180final`;

-- User information
create table `users`
(
	`id` int unsigned auto_increment,
	`username` varchar(32) unique not null,
	`first_name` varchar(64),
	`last_name` varchar(64),
	`email_address` varchar(64) unique not null,
	`password` blob not null,

	primary key (`id`)
);

create table `customers`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict
);

create table `vendors`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict
);

create table `admins`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict
);

-- Product information
create table `products`
(
	`id` int unsigned auto_increment,
	`name` varchar(128) not null,
	`description` text not null,
	`vendor_id` int unsigned not null,
	`quantity` int unsigned not null,
	`price` decimal(8, 2) not null,

	primary key (`id`),
	foreign key (`vendor_id`) references `vendors` (`id`) on update restrict,
	unique (`name`, `vendor_id`),

	constraint check
	(
		`price` >= 0
	)
);

create table `deleted_products`
(
	`product_id` int unsigned,

	primary key (`product_id`),
	foreign key (`product_id`) references `products` (`id`) on delete restrict on update restrict
);

create table `product_warranty`
(
	`id` int unsigned auto_increment,
	`product_id` int unsigned not null,
	`coverage_days` int unsigned,
	`coverage_information` text,

	primary key (`id`),
	foreign key (`product_id`) references `products` (`id`) on delete restrict on update restrict
);

create table `deleted_warranty`
(
	`warranty_id` int unsigned,

	primary key (`warranty_id`),
	foreign key (`warranty_id`) references `product_warranty` (`id`) on delete restrict on update restrict
);

create table `product_images`
(
	`product_id` int unsigned,
	`image_data` varchar(255) not null,

	foreign key (`product_id`) references `products` (`id`) on delete restrict on update restrict
);

create table `product_discounts`
(
	`id` int unsigned auto_increment,
	`product_id` int unsigned,
	`discount` decimal(3, 2) not null,
	`start_date` datetime not null,
	`end_date` datetime,

	primary key (`id`),
	foreign key (`product_id`) references `products` (`id`) on delete restrict on update restrict,

	constraint check
	(
		`discount` between 0 and 1
	)
);

-- Cart and order information
create table `carts`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict
);

create table `cart_items`
(
	`id` int unsigned auto_increment,
	`cart_id` int unsigned,
	`product_id` int unsigned,
	`quantity` tinyint unsigned not null,
	`current_unit_price` decimal(8, 2) not null,
	`current_discount` decimal(3, 2) not null,

	primary key (`id`),
	foreign key (`cart_id`) references `carts` (`id`) on delete cascade on update restrict,
	foreign key (`product_id`) references `products` (`id`) on delete restrict on update restrict
);

create table `orders`
(
	`id` int unsigned auto_increment,
	`cart_id` int unsigned not null,
	`date` datetime not null,
	`price` decimal(16, 2) not null,
	`street` varchar(255) not null,
	`city` varchar(32) not null,
	`state` varchar(32) not null,
	`zip_code` varchar(10) not null,
	`country` varchar(16) not null,
	`payment_method` varchar(16) not null,
	`status` enum ( 'pending', 'confirmed', 'canceled', 'shipped', 'delivered' ) not null,

	primary key (`id`),
	foreign key (`cart_id`) references `carts` (`id`) on delete restrict on update restrict,
	unique (`cart_id`),

	constraint check
	(
		`price` >= 0
	)
);

create table `active_warranty`
(
	`warranty_id` int unsigned not null,
	`user_id` int unsigned not null,
	`order_id` int unsigned not null,
	`activation_date` date not null,
	`expiration_date` date,

	foreign key (`warranty_id`) references `product_warranty` (`id`) on delete restrict on update restrict,
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict,
	foreign key (`order_id`) references `orders` (`id`) on delete restrict on update restrict
);

-- Complaint information
create table `complaints`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,
	`order_id` int unsigned not null,
	`date` datetime not null,
	`title` varchar(255) not null,
	`description` text not null,
	`demand` enum ( 'return', 'refund', 'warranty' )  not null,
	`status` enum ( 'pending', 'reviewed', 'accepted', 'declined' ) not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on update restrict,
	foreign key (`order_id`) references `orders` (`id`) on update restrict on delete restrict
);

create table `complaint_images`
(
	`complaint_id` int unsigned not null,
	`image_data` varchar(255) not null,

	foreign key (`complaint_id`) references `complaints` (`id`) on delete cascade on update restrict
);

-- Review information
create table `reviews`
(
	`id` int unsigned auto_increment,
	`product_id` int unsigned not null,
	`user_id` int unsigned not null,
	`rating` decimal(1, 0) not null,
	`description` text not null,
	`date` datetime not null,

	primary key (`id`),
	foreign key (`product_id`) references `products` (`id`) on update restrict,
	foreign key (`user_id`) references `users` (`id`) on update restrict,

	constraint check
	(
		`rating` between 1 and 5
	)
);

create table `review_images`
(
	`review_id` int unsigned not null,
	`image_data` varchar(255) not null,

	foreign key (`review_id`) references `reviews` (`id`) on delete cascade on update restrict
);

-- Chat information
create table `chats`
(
	`id` int unsigned auto_increment,
	`user_id` int unsigned not null,
	`vendor_id` int unsigned not null,
	`admin_id` int unsigned not null,

	primary key (`id`),
	foreign key (`user_id`) references `users` (`id`) on update restrict,
	foreign key (`vendor_id`) references `vendors` (`id`) on update restrict,
	foreign key (`admin_id`) references `admins` (`id`) on update restrict
);

create table `chat_messages`
(
	`id` int unsigned auto_increment,
	`chat_id` int unsigned not null,
	`user_id` int unsigned not null,
	`content` text not null,

	primary key (`id`),
	foreign key (`chat_id`) references `chats` (`id`) on delete cascade on update restrict,
	foreign key (`user_id`) references `users` (`id`) on delete cascade on update restrict
);

create table `chat_attachments`
(
	`id` int unsigned auto_increment,
	`message_id` int unsigned not null,
	`content` varchar(255) not null,

	primary key (`id`),
	foreign key (`message_id`) references `chat_messages` (`id`) on delete cascade on update restrict
);
