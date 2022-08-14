import	React, {ReactElement}	from	'react';
import	{Card, Banner, DescriptionList}			from	'@yearn-finance/web-lib/components';

function	Content(): ReactElement {
	return (
		<div className={'w-full'}>
			<div className={'flex w-full flex-col gap-2'}>
				<h4 className={'mb-2'}>{'How to use'}</h4>
				<div className={'mb-6 space-y-2'}>
					<p className={'text-neutral-500'}>
						{'The web-lib contains components that can be used to build a new web application (website, dashboard, standalone, etc.), focused for the needs of Yearn Finance and the specificities of the web-3 ecosystem.'}
					</p>
					<p className={'text-neutral-500'}>
						{'The Lib is divided in various sub-sections: components, layouts, utils, contexts and hooks. With it, you should have everything you need to start working with Yearn and Ethereum, from the "Connect Wallet" to the designs of the buttons.'}
					</p>
					<p className={'text-neutral-500'}>
						{'You can now start playing by editing the `pages/index.tsx` file.'}
					</p>
				</div>
				<Card variant={'background'}>
					<DescriptionList
						options={[
							{title: 'Web-Lib Repo', details: 'https://web.ycorpo.com/'}, 
							{title: 'NextJs documentation', details: 'https://nextjs.org/'}
						]} />
				</Card>
			</div>
		</div>
	);
}

function	Index(): ReactElement {
	return (
		<section aria-label={'some default section'}>
			<div className={'mb-4'}>
				<Banner title={'Yearn Finance'}>
					<div className={'space-y-4'}>
						<p className={'text-primary-500'}>{'Yearn strategists and systems identify the optimal opportunities for yield in the market. Each Vault auto-compounds earned tokens, meaning Yearn reinvests earned tokens to generate additional earnings over time.'}</p>
						<p className={'text-primary-500'}>{'Vaults are a passive investing strategy, enabling people to put their capital to work via automation.'}</p>
						<p className={'text-primary-500'}>{'Enjoy the growth market!'}</p>
					</div>
				</Banner>
			</div>
			<Card>
				<Content />
			</Card>
		</section>
	);
}

export default Index;
