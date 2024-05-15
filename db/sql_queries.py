# SQL queries
get_abonent_by_phonenumber_query = '''select OD.DEVICE, OD.CLIENT_CODE, CS.CONTRACT_CODE, rtrim(CS.CONTRACT) as CONTRACT, coalesce(P.PEOPLE_NAME, F.JUR_FIRM_NAME) as NAME,
       S.STREET_PREFIX + rtrim(S.STREET_NAME) + ', ' + cast(A.HOUSE as varchar(10)) + A.HOUSE_POSTFIX
           + ' - ' + cast(OD.FLAT as varchar(10)) + OD.FLAT_POSTFIX as ADDRESS, CL.TYPE_CODE
from (select * from INTEGRAL..OTHER_DEVICES where TYPE_CODE = 17 and rtrim(DEVICE) like '%' + ? ) OD
join INTEGRAL..CONTRACTS CS on OD.CLIENT_CODE = CS.CLIENT_CODE
join INTEGRAL..CLIENTS CL on OD.CLIENT_CODE = CL.CLIENT_CODE and CS.CLIENT_CODE = CL.CLIENT_CODE
left join INTEGRAL..PEOPLES P on CL.PEOPLE_CODE = P.PEOPLE_CODE
left join INTEGRAL..FIRMS F on CL.FIRM_CODE = F.FIRM_CODE
left join INTEGRAL..ADDRESS A on OD.ADDRESS_CODE = A.ADDRESS_CODE
left join INTEGRAL..STREETS S on A.STREET_CODE = S.STREET_CODE
left join INTEGRAL..TOWNS T on S.TOWN_CODE = T.TOWN_CODE
group by OD.DEVICE, OD.CLIENT_CODE, CS.CONTRACT_CODE, rtrim(CS.CONTRACT), coalesce(P.PEOPLE_NAME, F.JUR_FIRM_NAME),
         S.STREET_PREFIX + rtrim(S.STREET_NAME) + ', ' + cast(A.HOUSE as varchar(10)) + A.HOUSE_POSTFIX
           + ' - ' + cast(OD.FLAT as varchar(10)) + OD.FLAT_POSTFIX, CL.TYPE_CODE'''

checkPhone = """select grant_phone
               from SV..TBP_TELEGRAM_BOT
			   where chat_id = ?
			"""
checkUserExists = """select E = case
					when exists(
								select    phonenumber
								from    SV..TBP_TELEGRAM_BOT
								where     user_id = ?
								)
					then 1
					else 0
					end"""

# addUser_query = """
# begin
# insert into
# SV..TBP_TELEGRAM_BOT(user_id,
#                      chat_id,
#                      phonenumber,
#                      contract_code,
#                      grant_phone,
#                      date,
#                      admin,
#                      manager,
#                      known_user,
#                      bot_blocked,
#                      wish_news
#                     )
# values
#                     (
#                     cast( ? as varchar(20)),
#                     cast( ? as varchar(20)),
#                     cast( ? as varchar(20)),
#                     ?,
#                     cast('1' as character(1)),
#                     getdate(), 0 , 0 , 1 , 0, 1
#                     )
# select 1 as RESULT
# end
# """

updateUser = """update SV..TBP_TELEGRAM_BOT
					set phonenumber = ?,
                    grant_phone = '1',
                    contract_code = ?,
                    known_user = 1
					where convert(bigint, user_id) = ? and convert(bigint, chat_id) = ?
			"""

update_unknown_user = """insert into SV..TBP_TELEGRAM_BOT(user_id, chat_id, phonenumber, known_user) values (?, ?, ?, 0)"""

delPhone = """update SV..TBP_TELEGRAM_BOT
					set grant_phone = '0'
					where phonenumber = ?"""

delUser = """delete from SV..TBP_TELEGRAM_BOT where chat_id = ?"""

getContractCode = \
	"""
					select cast(CL.CONTRACT_CODE as numeric(10,0)) as CONTRACT_CODE, cast(CS.CONTRACT as numeric(10,0)) as CONTRACT
					from INTEGRAL..OTHER_DEVICES OD
					join INTEGRAL..CONTRACT_CLIENTS CL on CL.CLIENT_CODE = OD.CLIENT_CODE
					join INTEGRAL..CONTRACTS CS on CS.CONTRACT_CODE = CL.CONTRACT_CODE
					where OD.DEVICE like '%'+right(cast(? as varchar), 10)+'%'
"""

getBalance_query = \
"""
declare     @CurDate datetime,
            @CurMonth datetime
select      @CurDate = getdate()
select      @CurMonth = M.MONTH
from        INT_PAYM..MONTH M
where       @CurDate >= M.MONTH and
            MONTH_NEXT > M.MONTH
select rtrim(CS.CONTRACT) as CONTRACT, CS.CONTRACT_CODE, isnull(TEM.TTL_EO_MONEY,0) as TTL_EO_MONEY,
       isnull(OUEM.OSNUSL_MONEY,0) as OSNUSL_MONEY,
       isnull(NCEO.PROPNACH_MONEY,0) as PROPNACH_MONEY,
       isnull(SELL.SELL_MONEY,0) as SELL_MONEY
from INTEGRAL..CONTRACTS CS
join (
-- сальдо текущее общее
    select      CONTRACT_CODE,sum(EO_MONEY) as TTL_EO_MONEY
    from        INT_PAYM..CONTRACT_STATE
    where       MONTH = @CurMonth
    group by    CONTRACT_CODE
    ) TEM on CS.CONTRACT_CODE = TEM.CONTRACT_CODE
join (
-- сальдо по 21 обороту
    select CONTRACT_CODE, sum(EO_MONEY) as OSNUSL_MONEY
    from INT_PAYM..CONTRACT_STATE
    where MONTH = @CurMonth and STATE_TYPE_CODE != 18
    group by CONTRACT_CODE
    ) OUEM on CS.CONTRACT_CODE = OUEM.CONTRACT_CODE
left join (
-- пропущенные начисления
    select CONTRACT_CODE, sum(MONEY) as PROPNACH_MONEY
    from INT_PAYM..CONTRACT_NOT_CALC
    where CALC_USE_FLAG = 0 and MONTH = @CurMonth
    group by CONTRACT_CODE
    ) NCEO on CS.CONTRACT_CODE = NCEO.CONTRACT_CODE
left join (
-- оборот рассрочки
    select ST.CONTRACT_CODE, sum(EO_MONEY) as SELL_MONEY
    from INT_PAYM..CONTRACT_STATE ST
             join INTEGRAL..CONTRACTS CS on ST.CONTRACT_CODE = CS.CONTRACT_CODE
    where MONTH = @CurMonth
      and STATE_TYPE_CODE = 18
    group by ST.CONTRACT_CODE
    ) SELL on CS.CONTRACT_CODE = SELL.CONTRACT_CODE
where CS.CONTRACT_CODE = (?)
group by CS.CONTRACT, CS.CONTRACT_CODE, TEM.TTL_EO_MONEY, OUEM.OSNUSL_MONEY, NCEO.PROPNACH_MONEY, SELL.SELL_MONEY
"""
getPayments = \
	'''
					declare     @CurDate datetime,
					            @CurMonth datetime
					select      @CurDate = getdate()
					select      @CurMonth = M.MONTH
					    from    INT_PAYM..MONTH M
					where       @CurDate >= M.MONTH and
					            MONTH_NEXT > M.MONTH
					select case
					            when datepart(mm,MONTH) = 1 then 'Январь' when datepart(mm,MONTH) = 2 then 'Февраль'
					            when datepart(mm,MONTH) = 3 then 'Март' when datepart(mm,MONTH) = 4 then 'Апрель'
					            when datepart(mm,MONTH) = 5 then 'Май' when datepart(mm,MONTH) = 6 then 'Июнь'
					            when datepart(mm,MONTH) = 7 then 'Июль' when datepart(mm,MONTH) = 8 then 'Август'
					            when datepart(mm,MONTH) = 9 then 'Сентябрь' when datepart(mm,MONTH) = 10 then 'Октябрь'
					            when datepart(mm,MONTH) = 11 then 'Ноябрь' when datepart(mm,MONTH) = 12 then 'Декабрь'
					        end,
					            sum(PAY_MONEY)
					    from    INT_PAYM..CONTRACT_PAYS
					where       MONTH >= dateadd(mm, -3, @CurDate) and
					            CONTRACT_CODE = (?) and
					            USED = 1
					group by    MONTH
					order by    datepart(mm,MONTH)
'''
last_payment_query = """
declare @CurMonth datetime, @CurDate datetime
select @CurDate = getdate()
select @CurMonth = M.MONTH
from INT_PAYM..MONTH M
where @CurDate >= M.MONTH and M.MONTH_NEXT >= M.MONTH
select B.user_id as USER_ID,
       sum(CP.PAY_MONEY) as PAY_MONEY,
       CP.TYPE_CODE,
       convert(smalldatetime, CP.PAY_DATE) as PAY_DATE,
       PT.TYPE_NAME
from INT_PAYM..CONTRACT_PAYS CP
join INT_PAYM..PAY_TYPES PT on CP.MONTH = PT.MONTH and CP.TYPE_CODE = PT.TYPE_CODE and PT.MONTH = @CurMonth
join SV..TBP_TELEGRAM_BOT B on CP.CONTRACT_CODE = B.contract_code
where CP.PAY_DATE >= dateadd(hh,-3, getdate()) and
      CP.MONTH = @CurMonth and
      CP.USED = 1 and
      CP.TYPE_CODE not in (162, 161, 160, 159, 152, 153, 136, 137, 125, 120,  15, 14, 4, 3, 2, 1)
group by B.user_id, CP.TYPE_CODE, convert(smalldatetime, CP.PAY_DATE), PT.TYPE_NAME
"""
set_payment_notice_status = \
	"""
					begin
					update SV..TBP_TELEGRAM_BOT
					set send_status = 1, send_time = ?, paid_money = ?
					from SV..TBP_TELEGRAM_BOT
					where cast(user_id as bigint) = ?
					end
					select 1 as UPDATE_RESULT
"""
getTechClaims_query = \
	"""
					select  A.APPL_ID as CLAIM_NUM,
					        rtrim(S.STATUS_NAME) as STATUS_NAME,
					        cast(A.APPL_DATE_CREATE as smalldatetime) as APPL_DATE_CREATE, -- Дата создания
					        A.APPL_DATE_RUN, -- Дата выполнения
					        B.CONTRACT_ID as CONTRACT,
					        CS.CONTRACT_CODE,
					        rtrim(C.ABON_NAME) as CLIENT_NAME,
					        rtrim(C.ABON_PHONE) as PHONE,
					        rtrim(D.ADDRESS_ABON_NAME) as ADDRESS_NAME,
					        rtrim(E.ERRORS_NAME) as ERROR_NAME,
					        rtrim(IP.INFO_PROBLEMS_NAME) as INFO_PROBLEMS_NAME
					from    SV..TIA_APPLICATION A
					        join SV..TIA_ABON C on A.APPL_ID = C.ABON_ID
					        join SV..TIA_INFO I on A.APPL_INFO_ID = I.INFO_ID
					        left join SV..TIA_STATUS S on A.APPL_STATUS_ID = S.STATUS_ID
					        left join SV..TIA_CONTRACT B on A.APPL_ID = B.CONTRACT_ABON_ID
					        left join SV..TIA_ADDRESS D on A.APPL_ID = D.ADDRESS_ABON_ID
					        left join SV..TIA_INFO_PROBLEMS IP on A.APPL_INFO_PROBLEMS_ID = IP.INFO_PROBLEMS_ID
					        left join SV..TIA_ERRORS E on A.APPL_ERRORS_ID = E.ERRORS_ID
					        join INTEGRAL..CONTRACTS CS on B.CONTRACT_ID = cast(CS.CONTRACT as int)
					where   A.APPL_DATE_CREATE >= dateadd(dd, -7, getdate()) and
					        CS.CONTRACT_CODE = ? and
					        A.APPL_DATE_CLOSE is null
"""

getContractCodeByUserId_query = \
	"""
					select contract_code as CONTRACT_CODE
					from SV..TBP_TELEGRAM_BOT
					where user_id = ?
"""

getLastTechClaims = \
	"""
					select  A.APPL_ID as CLAIM_NUM,
					rtrim(S.STATUS_NAME) as STATUS_NAME,
					cast(A.APPL_DATE_CREATE as smalldatetime) as APPL_DATE_CREATE, -- Дата создания
					A.APPL_DATE_RUN, -- Дата выполнения
					B.CONTRACT_ID as CONTRACT,
					CS.CONTRACT_CODE,
					rtrim(C.ABON_NAME) as CLIENT_NAME,
					rtrim(C.ABON_PHONE) as PHONE,
					rtrim(D.ADDRESS_ABON_NAME) as ADDRESS_NAME,
					rtrim(E.ERRORS_NAME) as ERROR_NAME,
					rtrim(IP.INFO_PROBLEMS_NAME) as INFO_PROBLEMS_NAME
					from    SV..TIA_APPLICATION A
					join SV..TIA_ABON C on A.APPL_ID = C.ABON_ID
					join SV..TIA_INFO I on A.APPL_INFO_ID = I.INFO_ID
					left join SV..TIA_STATUS S on A.APPL_STATUS_ID = S.STATUS_ID
					left join SV..TIA_CONTRACT B on A.APPL_ID = B.CONTRACT_ABON_ID
					left join SV..TIA_ADDRESS D on A.APPL_ID = D.ADDRESS_ABON_ID
					left join SV..TIA_INFO_PROBLEMS IP on A.APPL_INFO_PROBLEMS_ID = IP.INFO_PROBLEMS_ID
					left join SV..TIA_ERRORS E on A.APPL_ERRORS_ID = E.ERRORS_ID
					join INTEGRAL..CONTRACTS CS on B.CONTRACT_ID = cast(CS.CONTRACT as int)
					join SV..TBP_TELEGRAM_BOT TTB on CS.CONTRACT_CODE = TTB.contract_code
					where   A.APPL_DATE_CREATE >= dateadd(ss, -120, getdate()) and
					        A.APPL_DATE_CLOSE is null
"""
getClientCodeByContractCode = \
	"""
					select CL.CLIENT_CODE, CL.TYPE_CODE
					from INTEGRAL..CONTRACT_CLIENTS CCL
					join INTEGRAL..CLIENTS CL on CCL.CLIENT_CODE = CL.CLIENT_CODE
					where CCL.CONTRACT_CODE = ?
"""

PromisedPayDate = \
"""
					select cast(DATE_CHANGE as smalldatetime) as DATE_CHANGE
					from INTEGRAL..CLIENT_PROPERTIES
					where CLIENT_CODE = ? and PROP_CODE = 823
"""

getInetAccountPassword_query = \
"""
					select rtrim(OD.LOGIN) as LOGIN, MEDIATE.dbo.ContractPasswordDecode(rtrim(OD.PASSWORD)) as PASSWORD
					from INTEGRAL..OTHER_DEVICES OD
					join INTEGRAL..CONTRACT_CLIENTS CCL on OD.CLIENT_CODE = CCL.CLIENT_CODE
					where CCL.CONTRACT_CODE = ? and OD.TYPE_CODE = 14
"""

getPersonalAreaPassword_query = \
"""
					select rtrim(PIN) as PIN, rtrim(PIN_PASSWORD) as PIN_PASSWORD
					from INTEGRAL..CLIENT_PINS
					where CLIENT_CODE = ?
"""

get_admin_query = '''
select user_id from SV..TBP_TELEGRAM_BOT where admin = 1
'''

get_manager_query = '''
select user_id from SV..TBP_TELEGRAM_BOT where manager = 1
'''

get_all_users_query = """
select user_id from SV..TBP_TELEGRAM_BOT
"""

get_known_user_query = """
select user_id from SV..TBP_TELEGRAM_BOT where known_user = 1
"""

get_all_unbanned_users_query = """
select user_id from SV..TBP_TELEGRAM_BOT where bot_blocked = 0 and known_user = 1
"""

get_all_known_unbanned_users_query = """
select user_id from SV..TBP_TELEGRAM_BOT where bot_blocked = 0 and known_user = 1 and wish_news = 1
"""

set_known_user_query = """
declare @user_id varchar(20)
select @user_id = ?
if EXISTS(select 1 from SV..TBP_TELEGRAM_BOT where user_id = @user_id)
    begin
        if EXISTS(select 1 from SV..TBP_TELEGRAM_BOT where user_id = @user_id and admin = 0)
        begin
            update SV..TBP_TELEGRAM_BOT
            set admin = 0, manager = 0, known_user = 1
            where user_id = @user_id
            select 1 as RESULT
        end
        else
        select 2 as RESULT
    end
if NOT EXISTS(select 1 from SV..TBP_TELEGRAM_BOT where user_id = @user_id)
    begin
        select 0 as RESULT
    end
"""

get_phonenumber_by_user_id_query = """
select phonenumber from SV..TBP_TELEGRAM_BOT where cast(user_id as bigint) = ?
"""

get_client_code_by_contract_code = '''
select CL.CLIENT_CODE, CC.CONTRACT_CODE, CL.TYPE_CODE
from INTEGRAL..CONTRACT_CLIENTS CC
join INTEGRAL..CLIENTS CL on CC.CLIENT_CODE = CL.CLIENT_CODE
where CC.CONTRACT_CODE in ( ? )
'''
# TODO: переделать на хранимку
add_client_properties_w_commentary = """
declare @ClientCode int, @PropCode int, @Commentary univarchar(4096)
select @ClientCode = ?, @PropCode = ?, @Commentary = ?
if EXISTS(select 1 from INTEGRAL..CLIENTS where CLIENT_CODE = @ClientCode)
    begin
        if EXISTS(select 1 from SV..TBP_TELEGRAM_BOT where user_id = @ClientCode and action_name is null)
        begin
            insert into INTEGRAL..CLIENT_PROPERTIES(CLIENT_CODE, PROP_CODE, QUANTITY, DATE_OPERATE, COMMENTARY, USER_CODE, DATE_CHANGE)
            values (@ClientCode, @PropCode, 1, getdate(), @Commentary, 139, getdate())
            select 1 as RESULT
        end
        else
        select 2 as RESULT
    end
if NOT EXISTS(select 1 from INTEGRAL..CLIENTS where CLIENT_CODE = @ClientCode)
    begin
        select 0 as RESULT
    end
"""
# TODO: переделать на хранимку
add_client_properties_wo_commentary = """
declare @ClientCode int, @PropCode int
select @ClientCode = ?, @PropCode = ?
if EXISTS(select 1 from INTEGRAL..CLIENTS where CLIENT_CODE = @ClientCode)
    begin
        if EXISTS(select 1 from SV..TBP_TELEGRAM_BOT where user_id = @ClientCode and action_name is null)
        begin
            insert into INTEGRAL..CLIENT_PROPERTIES(CLIENT_CODE, PROP_CODE, QUANTITY, DATE_OPERATE, COMMENTARY, USER_CODE, DATE_CHANGE)
            values (@ClientCode, @PropCode, 1, getdate(), null, 139, getdate())
            select 1 as RESULT
        end
        else
        select 2 as RESULT
    end
if NOT EXISTS(select 1 from INTEGRAL..CLIENTS where CLIENT_CODE = @ClientCode)
    begin
        select 0 as RESULT
    end
"""

pay_time_query ="""
select isnull(send_time, '1900-01-01 00:00:00') as send_time, isnull(paid_money, 0) as paid_money
from SV..TBP_TELEGRAM_BOT
where convert(bigint, user_id) = ?
"""

get_surveys_list = """
select SURVEY_ID, SURVEY_NAME, MAX_GRADE
from SV..TBP_TELEGRAM_SURVEYS
"""

insert_survey_grade = """
begin tran
INSERT INTO SV..TBP_TELEGRAM_SURVEYS_GRADE(SURVEY_ID, USER_ID, GRADE, DATE)
VALUES (?, ?, ?, GETDATE())
IF @@ROWCOUNT > 0
    BEGIN
        commit tran
        SELECT 1 AS result
    end
ELSE
    BEGIN
        rollback tran
        SELECT 0 AS result
    END
"""

check_access_survey_for_user = """
select S.SURVEY_ID, S.SURVEY_SHORT_NAME, S.SURVEY_LONG_NAME,S.MAX_GRADE
from SV..TBP_TELEGRAM_SURVEYS S
left join SV..TBP_TELEGRAM_SURVEYS_GRADE G on S.SURVEY_ID = G.SURVEY_ID
where NOT EXISTS(select USER_ID from SV..TBP_TELEGRAM_SURVEYS_GRADE G1 where G.SURVEY_ID = G1.SURVEY_ID and G1.USER_ID = ?)
if @@rowcount = 0
	begin
		select null
	end
"""

survey_long_name = """
select SURVEY_LONG_NAME
from SV..TBP_TELEGRAM_SURVEYS
where SURVEY_ID = ?
"""

all_voted_surveys_for_user = """
select S.SURVEY_SHORT_NAME, S.SURVEY_LONG_NAME, G.GRADE, cast(G.DATE as smalldatetime) as DATE
from SV..TBP_TELEGRAM_SURVEYS S
join SV..TBP_TELEGRAM_SURVEYS_GRADE G on S.SURVEY_ID = G.SURVEY_ID
where G.USER_ID = ?
"""