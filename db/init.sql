create table if not exists tbl_transaction_flows (
    id serial primary key,
    name varchar(100) not null unique
);

create table if not exists tbl_transaction_services (
    id serial primary key,
    name varchar(100) not null,
    rank integer not null,
    regexp text not null,
    flow_id integer not null references flow(id)
);

create table if not exists tbl_transaction_status (
    id serial primary key,
    transaction_id varchar(200) not null,
    flow varchar(100) not null,
    service varchar(100) not null,
    status varchar(20) not null,
    status_reason text,
    created_on timestamp not null,
    constraint uq_transaction_status_txn_flow_service
        unique (transaction_id, flow, service)
);

create index if not exists idx_transaction_status_transaction_id
    on tbl_transaction_status(transaction_id);

create index if not exists idx_transaction_status_created_on
    on tbl_transaction_status(created_on);


insert into tbl_transaction_flows (name)
values ('mpesa_c2b')
on conflict (name) do nothing;

insert into tbl_transaction_services (name, rank, regexp, flow_id)
select
    'stk-push-service',
    1,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"message":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from tbl_transaction_services s
    where s.name = 'stk-push-service'
      and s.flow_id = flow.id
);

insert into tbl_transaction_services (name, rank, regexp, flow_id)
select
    'mpesa-callback-service',
    2,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"status_reason":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from tbl_transaction_services s
    where s.name = 'mpesa-callback-service'
      and s.flow_id = flow.id
);

insert into tbl_transaction_services (name, rank, regexp, flow_id)
select
    'credit-account-service',
    3,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"status_reason":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from tbl_transaction_services s
    where s.name = 'credit-account-service'
      and s.flow_id = flow.id
);

insert into tbl_transaction_services (name, rank, regexp, flow_id)
select
    'notification-service',
    4,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"message":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from tbl_transaction_services s
    where s.name = 'notification-service'
      and s.flow_id = flow.id
);