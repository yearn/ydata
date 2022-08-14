import	React, {ReactElement}				from	'react';
import	Link								from	'next/link';
import	{AppProps}							from	'next/app';
import	{Header}							from	'@yearn-finance/web-lib/layouts';
import	{WithYearn}							from	'@yearn-finance/web-lib/contexts';
import	{useBalance}						from	'@yearn-finance/web-lib/hooks';
import	LogoYearn							from	'components/icons/LogoYearn';
import	Footer								from	'components/StandardFooter';
import	Meta								from	'components/Meta';

import	'../style.css';

function	AppHeader(): ReactElement {
	const	[shouldDisplayPrice, set_shouldDisplayPrice] = React.useState(true);
	const	{data: YFIBalance} = useBalance({
		for: '0x7a1057e6e9093da9c1d4c1d049609b6889fc4c67',
		token: '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e'
	});

	return (
		<Header>
			<div className={'flex-row-center w-full justify-between pr-4'}>
				<Link href={'/'}>
					<div className={'flex cursor-pointer flex-row items-center space-x-4'}>
						<LogoYearn />
						<h1>{'Yearn'}</h1>
					</div>
				</Link>
				<div className={'hidden flex-row items-center space-x-6 md:flex'}>
					<div
						className={'cursor-pointer'}
						onClick={(): void => set_shouldDisplayPrice(!shouldDisplayPrice)}>
						{shouldDisplayPrice ? (
							<p className={'text-primary-500'}>
								{`YFI $ ${YFIBalance.normalizedPrice}`}
							</p>
						) : (
							<p className={'text-primary-500'}>
								{`Balance: ${YFIBalance.normalized} YFI`}
							</p>
						)}
					</div>
				</div>
			</div>
		</Header>
	);
}

function	MyApp(props: AppProps): ReactElement {
	const	{Component, router, pageProps} = props;
	
	return (
		<WithYearn
			options={{
				web3: {
					shouldUseWallets: true,
					shouldUseStrictChainMode: false,
					defaultChainID: 1,
					supportedChainID: [1, 250, 42161, 1337, 31337]
				}
			}}>
			<React.Fragment>
				<Meta />
				<div id={'app'} className={'mx-auto mb-0 grid max-w-6xl grid-cols-12 flex-col gap-x-4 md:flex-row'}>
					<div className={'col-span-12 flex min-h-[100vh] w-full flex-col px-4'}>
						<AppHeader />
						<Component
							key={router.route}
							router={router}
							{...pageProps} />
						<Footer />
					</div>
				</div>
			</React.Fragment>
		</WithYearn>
	);
}

export default MyApp;
