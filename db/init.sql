create table if not exists flow (
    id serial primary key,
    name varchar(100) not null unique
);

create table if not exists service (
    id serial primary key,
    name varchar(100) not null,
    rank integer not null,
    regexp text not null,
    flow_id integer not null references flow(id)
);

create table if not exists transaction_status (
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
    on transaction_status(transaction_id);

create index if not exists idx_transaction_status_created_on
    on transaction_status(created_on);

create index if not exists idx_transaction_status_txn_flow_service
    on transaction_status(transaction_id, flow, service);

insert into flow (name)
values ('mpesa_c2b')
on conflict (name) do nothing;

insert into service (name, rank, regexp, flow_id)
select
    'stk-push-service',
    1,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"message":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from service s
    where s.name = 'stk-push-service'
      and s.flow_id = flow.id
);

insert into service (name, rank, regexp, flow_id)
select
    'mpesa-callback-service',
    2,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"status_reason":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from service s
    where s.name = 'mpesa-callback-service'
      and s.flow_id = flow.id
);

insert into service (name, rank, regexp, flow_id)
select
    'credit-account-service',
    3,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"status_reason":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from service s
    where s.name = 'credit-account-service'
      and s.flow_id = flow.id
);

insert into service (name, rank, regexp, flow_id)
select
    'notification-service',
    4,
    '"flow":"(?P<flow>[^"]+)".*?"service":"(?P<service>[^"]+)".*?"transaction_id":"(?P<transactionId>[^"]+)".*?"status":"(?P<status>[^"]+)".*?"message":"(?P<statusReason>[^"]+)"',
    id
from flow
where name = 'mpesa_c2b'
and not exists (
    select 1 from service s
    where s.name = 'notification-service'
      and s.flow_id = flow.id
);