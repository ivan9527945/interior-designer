import NextAuth from "next-auth";

/**
 * next-auth v5 設定。Sprint 1 骨架：providers 為空陣列，
 * Sprint 4 會加 Keycloak provider。
 */
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [],
  session: { strategy: "jwt" },
  pages: { signIn: "/login" },
});
