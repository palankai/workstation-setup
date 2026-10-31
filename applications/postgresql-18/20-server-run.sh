# With the `server` option; already running is fine
case " $APP_OPTIONS " in
  *" server "*) brew services start postgresql@18 ;;
esac
