subroutine prepare_daily(daily_config,config_paths,config_attributes,task)

  implicit none

  character*1024 :: daily_config
  character(len=256) :: config_paths,config_attributes
  character(len=1536) :: command_line

  integer :: estat,cstat,task
  character(len=1024) :: cmsg
  character(len=10) :: ctask

  Write( ctask, '(i10)' ) task


  command_line="/perm/ms/de/sf7/cschlund/ecflow_cc4cl_proc/src/process_single_day.ksh "&
       & //trim(adjustl(config_paths))//" "//trim(adjustl(config_attributes))//" "//trim(adjustl(daily_config))&
       & //" "//trim(adjustl(ctask))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)

end subroutine prepare_daily
