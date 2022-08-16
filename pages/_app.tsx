import { WithYearn } from '@yearn-finance/web-lib/contexts'
import { Header } from '@yearn-finance/web-lib/layouts'
import LogoYearn from 'components/icons/LogoYearn'
import Meta from 'components/Meta'
import Footer from 'components/StandardFooter'
import { AppProps } from 'next/app'
import Link from 'next/link'
import React, { ReactElement } from 'react'

import '../style.css'

function AppHeader(): ReactElement {
  return (
    <Header shouldUseNetworks={false} shouldUseWallets={false}>
      <div className={'flex-row-center w-full justify-between pr-4'}>
        <Link href={'/'}>
          <div className={'flex cursor-pointer flex-row items-center space-x-4'}>
            <LogoYearn />
            <h1>{'Messari Frontier Web'}</h1>
          </div>
        </Link>
      </div>
    </Header>
  )
}

function MyApp(props: AppProps): ReactElement {
  const { Component, router, pageProps } = props

  return (
    <WithYearn
      options={{
        web3: {
          shouldUseWallets: false,
          shouldUseStrictChainMode: false,
          defaultChainID: 1,
          supportedChainID: [1, 250, 42161, 1337, 31337],
        },
      }}
    >
      <React.Fragment>
        <Meta />
        <div id={'app'} className={'mx-auto mb-0 grid max-w-6xl grid-cols-12 flex-col gap-x-4 md:flex-row'}>
          <div className={'col-span-12 flex min-h-[100vh] w-full flex-col px-4'}>
            <AppHeader />
            <Component key={router.route} router={router} {...pageProps} />
            <Footer />
          </div>
        </div>
      </React.Fragment>
    </WithYearn>
  )
}

export default MyApp
