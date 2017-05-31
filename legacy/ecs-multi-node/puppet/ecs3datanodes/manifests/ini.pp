class ecs3datanodes {
# include ecs3datanodes::configure

  if $checkecsfile{
    notify {"ECS Container is running":}
  }
   else
  {
    notify {"Installing ECS Software":}
    include ecs3datanodes::configure
  }

}
