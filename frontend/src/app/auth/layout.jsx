import {AuthLayout} from "@/layouts/auth";
import {GuestGuard} from "@/auth/guard"

export default function Layout({children}) {
    return <GuestGuard><AuthLayout>{children}</AuthLayout></GuestGuard>
}