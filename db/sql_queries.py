# SQL queries
get_abonent_by_phonenumber_query = '''select DEVICE, OD.CLIENT_CODE, CONTRACT_CODE, rtrim(CONTRACT) as CONTRACT, coalesce(P.PEOPLE_NAME, F.JUR_FIRM_NAME) as NAME,
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
group by DEVICE, OD.CLIENT_CODE, CONTRACT_CODE, rtrim(CONTRACT), coalesce(P.PEOPLE_NAME, F.JUR_FIRM_NAME),
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
                    contract_code = cast(? as int)
					where user_id = ? and chat_id = ?"""

update_unknown_user = """insert into SV..TBP_TELEGRAM_BOT(user_id, chat_id, phonenumber, known_user) values (?, ?, ?, 0)"""

delPhone = """update SV..TBP_TELEGRAM_BOT
					set grant_phone = '0'
					where phonenumber = ?"""

delUser = """delete from SV.dbo.TBP_TELEGRAM_BOT where chat_id = ?"""

getContractCode = \
	"""
					select cast(CL.CONTRACT_CODE as numeric(10,0)) as CONTRACT_CODE, cast(CS.CONTRACT as numeric(10,0)) as CONTRACT
					from INTEGRAL..OTHER_DEVICES OD
					join INTEGRAL..CONTRACT_CLIENTS CL on CL.CLIENT_CODE = OD.CLIENT_CODE
					join INTEGRAL..CONTRACTS CS on CS.CONTRACT_CODE = CL.CONTRACT_CODE
					where DEVICE like '%'+right(cast(? as varchar), 10)+'%'
"""

getBalance_query = \
	"""
					declare     @CurDate datetime,
                                @CurMonth datetime
                    select      @CurDate = getdate()
                    select      @CurMonth = M.MONTH
                        from    INT_PAYM..MONTH M
                    where       @CurDate >= M.MONTH and
                                MONTH_NEXT > M.MONTH
                    select      sum(EO_MONEY) as EO_MONEY
                        from    INT_PAYM..CONTRACT_STATE
                    where       MONTH = dateadd(mm,0,@CurMonth) and
                                CONTRACT_CODE = (?)
                    group by    CONTRACT_CODE
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
getLastPayment = \
	'''
					select B.user_id, sum(CP.PAY_MONEY) as PAY_MONEY
					from INT_PAYM..CONTRACT_PAYS CP
					join SV..TBP_TELEGRAM_BOT B on CP.CONTRACT_CODE = B.contract_code
					where CP.PAY_DATE >= dateadd(ss,-120, getdate()) and CP.USED = 1
					group by B.user_id
'''
setSendStatus = \
	"""
					update SV..TBP_TELEGRAM_BOT
					set send_status = (?), send_time = (?), paid_money = (?)
					from SV..TBP_TELEGRAM_BOT
					where user_id = (?)
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
					where CONTRACT_CODE = ?
"""

PromisedPayDate = \
"""
					select cast(DATE_CHANGE as smalldatetime) as DATE_CHANGE
					from INTEGRAL..CLIENT_PROPERTIES
					where CLIENT_CODE = ? and PROP_CODE = 823
"""

getInetAccountPassword_query = \
"""
					select rtrim(LOGIN) as LOGIN, MEDIATE.dbo.ContractPasswordDecode(rtrim(PASSWORD)) as PASSWORD
					from INTEGRAL..OTHER_DEVICES OD
					join INTEGRAL..CONTRACT_CLIENTS CCL on OD.CLIENT_CODE = CCL.CLIENT_CODE
					where CONTRACT_CODE = ? and OD.TYPE_CODE = 14
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
select user_id from SV..TBP_TELEGRAM_BOT where bot_blocked = 0
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
select CL.CLIENT_CODE, CONTRACT_CODE, TYPE_CODE
from INTEGRAL..CONTRACT_CLIENTS CC
join INTEGRAL..CLIENTS CL on CC.CLIENT_CODE = CL.CLIENT_CODE
where CONTRACT_CODE in ( ? )
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