import { AuthGuard } from "@/auth/guard"
export default function Layout({children}){
    return <AuthGuard>{children}</AuthGuard>
}